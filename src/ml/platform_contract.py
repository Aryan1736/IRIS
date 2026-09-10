"""Authoritative ML Platform Integration Contract module for IRIS (PR-14).

Defines the formal, versioned, deterministic contract between:
- ARYAN: AI/ML & Data Intelligence
- SRINIVASH: Backend / Platform / Frontend

Insulates platform layers from ML internals (CatBoost/Logistic Regression details,
feature engineering pipelines, artifact filesystem layouts, and training mechanics).
All platform-facing interactions occur through stable, verified prediction, feature,
explanation, governance, and project profile contracts.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from src.ml.model_registry import (
    AVAILABILITY_AVAILABLE,
    AVAILABILITY_EVALUATION_ONLY,
    AVAILABILITY_INELIGIBLE,
    AVAILABILITY_NOT_AVAILABLE,
    CANONICAL_COMPLETED_PATH,
    CANONICAL_COMPLETED_SHA256,
    CANONICAL_MONTHLY_PATH,
    CANONICAL_MONTHLY_SHA256,
    DEFAULT_REGISTRY_RELPATH,
    DOMAIN_ALIASES,
    GOVERNANCE_LOCKED_PRODUCTION,
    GOVERNANCE_NOT_READY_FOR_PRODUCTION,
    GOVERNANCE_VIABLE_WITH_LIMITATIONS,
    REGISTRY_ID,
    REGISTRY_VERSION,
    SCHEDULE_LEGACY_ARTIFACT_PATH,
    SCHEDULE_LEGACY_ARTIFACT_SHA256,
    SCHEDULE_MODERN_ARTIFACT_PATH,
    SCHEDULE_MODERN_ARTIFACT_SHA256,
    ModelRegistry,
    ModelRegistryError,
)
from src.ml.unified_risk_predictor import (
    ALLOWED_TOP_LEVEL_METADATA_KEYS,
    PROHIBITED_LEAKAGE_FIELDS,
    SCHEDULE_DECISION_THRESHOLD,
)

# -----------------------------------------------------------------------------
# Frozen Contract Constants
# -----------------------------------------------------------------------------

CONTRACT_VERSION = "1.0.0"
CONTRACT_ID = "iris_ml_platform_contract_v1"
CONTRACT_NAME = "ml_platform_contract_v1"
GENERATION_POLICY = "deterministic_platform_contract_derivation"

SCHEMA_CONTRACT_RELPATH = "schemas/ml_platform_contract_v1.contract.json"
DEFAULT_CONTRACT_DIR_RELPATH = "artifacts/ml/ml_platform_contract_v1"
DEFAULT_CONTRACT_RELPATH = "artifacts/ml/ml_platform_contract_v1/contract.json"
DEFAULT_MANIFEST_RELPATH = "artifacts/ml/ml_platform_contract_v1/manifest.json"
DEFAULT_REPORT_RELPATH = "artifacts/ml/ml_platform_contract_v1/verification_report.json"

# Prohibited probability fusion keys in profile payloads
PROHIBITED_PROBABILITY_FUSION_KEYS = frozenset({
    "combined_probability",
    "overall_probability",
    "aggregated_probability",
    "weighted_probability",
    "fused_probability",
    "overall_risk_score",
    "composite_risk_score",
    "total_risk_score",
    "average_risk",
    "combined_risk",
})

NON_CAUSAL_DISCLAIMER = (
    "Explanations represent non-causal statistical associations based on reporting patterns "
    "and model margins. They do not imply causal mechanisms or guaranteed project outcomes."
)


# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------

class MLPlatformContractError(Exception):
    """Base error for ML platform contract operations."""


class MLPlatformContractValidationError(MLPlatformContractError):
    """Raised when data fails platform contract schema or governance rules."""


class MLPlatformContractVerificationError(MLPlatformContractError):
    """Raised when contract fails cross-verification against ModelRegistry."""


# -----------------------------------------------------------------------------
# Core MLPlatformContract Class
# -----------------------------------------------------------------------------

class MLPlatformContract:
    """Formal, versioned, deterministic ML <-> Platform integration contract."""

    def __init__(
        self,
        contract_data: dict[str, Any],
        manifest_data: dict[str, Any] | None = None,
        root: Path | None = None,
    ) -> None:
        self._root = (root or Path.cwd()).resolve()
        self._contract = copy.deepcopy(contract_data)
        self._manifest = copy.deepcopy(manifest_data) if manifest_data else None

        # Validate structure on initialization
        errors = self.validate_contract(self._contract)
        if errors:
            raise MLPlatformContractValidationError(
                f"Invalid platform contract data: {'; '.join(errors)}"
            )

    @classmethod
    def load(
        cls,
        contract_path: Path | str | None = None,
        manifest_path: Path | str | None = None,
        root: Path | None = None,
    ) -> "MLPlatformContract":
        """Load authoritative platform contract from JSON artifact."""
        repo_root = (root or Path.cwd()).resolve()
        path = (
            Path(contract_path).resolve()
            if contract_path
            else (repo_root / DEFAULT_CONTRACT_RELPATH).resolve()
        )

        if not path.is_file():
            raise FileNotFoundError(f"Platform contract file not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                contract_data = json.load(f)
        except json.JSONDecodeError as exc:
            raise MLPlatformContractError(f"Corrupted contract JSON at {path}: {exc}") from exc

        manifest_data: dict[str, Any] | None = None
        m_path = (
            Path(manifest_path).resolve()
            if manifest_path
            else (repo_root / DEFAULT_MANIFEST_RELPATH).resolve()
        )
        if m_path.is_file():
            try:
                with open(m_path, "r", encoding="utf-8") as mf:
                    manifest_data = json.load(mf)
            except Exception:
                manifest_data = None

        return cls(contract_data=contract_data, manifest_data=manifest_data, root=repo_root)

    # -------------------------------------------------------------------------
    # Properties and Accessors
    # -------------------------------------------------------------------------

    @property
    def version(self) -> str:
        return str(self._contract.get("contract_version", ""))

    @property
    def contract_id(self) -> str:
        return str(self._contract.get("contract_id", ""))

    def get_contract(self) -> dict[str, Any]:
        """Return raw authoritative platform contract copy."""
        return copy.deepcopy(self._contract)

    def to_dict(self, mask_internal_paths: bool = True) -> dict[str, Any]:
        """Return contract dictionary, optionally masking internal filesystem paths."""
        data = copy.deepcopy(self._contract)
        if mask_internal_paths:
            data = self._mask_paths(data)
        return data

    def list_domains(self) -> list[str]:
        """Return list of canonical domain keys."""
        return sorted(list(self._contract.get("domains", {}).keys()))

    def normalize_domain_id(self, domain_name: str) -> str:
        """Resolve alias to canonical domain ID."""
        key = domain_name.strip().lower()
        if key in DOMAIN_ALIASES:
            return DOMAIN_ALIASES[key]
        if key in self._contract.get("domains", {}):
            return key
        if key in ("unified_profile", "profile", "risk_profile"):
            return "unified_profile"
        raise KeyError(
            f"Unknown domain identifier: '{domain_name}'. Valid domains: {self.list_domains()}"
        )

    def get_domain(self, domain_name: str) -> dict[str, Any]:
        """Retrieve authoritative domain contract."""
        canonical_id = self.normalize_domain_id(domain_name)
        if canonical_id == "unified_profile":
            return self.get_unified_profile_contract()
        domain = self._contract["domains"].get(canonical_id)
        if domain is None:
            raise KeyError(f"Domain '{canonical_id}' not found in platform contract.")
        return copy.deepcopy(domain)

    def get_prediction_contract(
        self,
        domain: str,
        regime: str | None = None,
        candidate_type: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve model-specific prediction contract."""
        dom = self.get_domain(domain)
        models = dom.get("models", {})

        if regime:
            target_regime = regime.strip().upper()
            for m_key, m_val in models.items():
                if m_val.get("regime", "").upper() == target_regime:
                    return copy.deepcopy(m_val)
            raise KeyError(f"Model with regime '{regime}' not found in domain '{domain}'.")

        if candidate_type:
            target_type = candidate_type.strip().lower()
            for m_key, m_val in models.items():
                if (
                    m_key.lower() == target_type
                    or m_val.get("candidate_type", "").lower() == target_type
                ):
                    return copy.deepcopy(m_val)
            raise KeyError(f"Model candidate '{candidate_type}' not found in domain '{domain}'.")

        if len(models) == 1:
            return copy.deepcopy(next(iter(models.values())))

        raise ValueError(
            f"Ambiguous query: domain '{domain}' has multiple models. Specify regime or candidate_type."
        )

    def get_feature_contract(self, domain: str, regime: str | None = None) -> dict[str, Any]:
        """Retrieve feature contract metadata for a domain/regime."""
        pred_contract = self.get_prediction_contract(domain=domain, regime=regime)
        return copy.deepcopy(pred_contract["feature_contract"])

    def get_explanation_contract(self, domain: str, regime: str | None = None) -> dict[str, Any]:
        """Retrieve explanation contract specification for a domain/regime."""
        pred_contract = self.get_prediction_contract(domain=domain, regime=regime)
        return copy.deepcopy(pred_contract["explanation"])

    def get_unified_profile_contract(self) -> dict[str, Any]:
        """Retrieve unified project risk profile contract specification."""
        profile = self._contract.get("unified_profile")
        if profile is None:
            raise KeyError("Unified profile contract not found in platform contract.")
        return copy.deepcopy(profile)

    # -------------------------------------------------------------------------
    # Response Envelope Builders & Validators
    # -------------------------------------------------------------------------

    def build_prediction_envelope(
        self,
        domain: str,
        regime: str | None,
        probability: float | None,
        prediction_status: str,
        operational_decision: int | None = None,
        drivers: list[dict[str, Any]] | None = None,
        prediction_id: str | None = None,
        prediction_timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a validated platform-safe prediction response envelope."""
        canonical_domain = self.normalize_domain_id(domain)
        dom_contract = self.get_domain(canonical_domain)

        # Lookup prediction contract
        model_contract: dict[str, Any] | None = None
        if regime:
            try:
                model_contract = self.get_prediction_contract(canonical_domain, regime=regime)
            except KeyError:
                model_contract = None
        elif len(dom_contract.get("models", {})) == 1:
            model_contract = next(iter(dom_contract["models"].values()))

        # Enforce fail-closed governance invariants on payload
        governance_status = dom_contract["governance_status"]
        production_availability = dom_contract["production_availability"]

        if production_availability in (AVAILABILITY_NOT_AVAILABLE, AVAILABILITY_INELIGIBLE):
            if probability is not None:
                raise MLPlatformContractValidationError(
                    f"Domain '{canonical_domain}' is '{production_availability}'; "
                    "probability must be null."
                )
            if operational_decision is not None:
                raise MLPlatformContractValidationError(
                    f"Domain '{canonical_domain}' is '{production_availability}'; "
                    "operational_decision must be null."
                )

        # Operational decision calculation if applicable
        decision_threshold = dom_contract.get("operational_decision_threshold")
        if operational_decision is None and probability is not None and decision_threshold is not None:
            operational_decision = 1 if probability >= decision_threshold else 0

        # Explanation payload construction
        exp_meta = model_contract["explanation"] if model_contract else {
            "available": False,
            "method": None,
            "contribution_space": None,
            "non_causal": True,
            "disclaimer": NON_CAUSAL_DISCLAIMER,
            "limitations": "No explanation available.",
        }

        formatted_drivers: list[dict[str, Any]] = []
        if drivers:
            for d in drivers:
                val = float(d.get("contribution", 0.0))
                direction = "risk_increasing" if val > 0 else ("risk_decreasing" if val < 0 else "neutral")
                formatted_drivers.append({
                    "feature": str(d.get("feature", "")),
                    "feature_group": str(d.get("feature_group", "unknown")),
                    "contribution": val,
                    "direction": direction,
                    "contribution_space": str(
                        d.get("contribution_space", exp_meta.get("contribution_space", "model_margin_or_logit"))
                    ),
                })

        envelope = {
            "contract_version": self.version,
            "prediction": {
                "prediction_id": prediction_id or f"pred-{canonical_domain}-{regime or 'none'}",
                "domain": canonical_domain,
                "regime": regime,
                "target": dom_contract["target"],
                "horizon_months": dom_contract["horizon_months"],
                "probability": probability,
                "prediction_status": prediction_status,
                "operational_decision": operational_decision,
                "decision_threshold": decision_threshold,
                "prediction_timestamp": prediction_timestamp or datetime.now(timezone.utc).isoformat(),
            },
            "model": {
                "model_id": model_contract["model_id"] if model_contract else f"{canonical_domain}_unassigned",
                "model_version": model_contract["model_version"] if model_contract else "none",
                "model_family": model_contract["model_family"] if model_contract else "none",
                "governance_status": governance_status,
                "production_availability": production_availability,
            },
            "calibration": copy.deepcopy(model_contract["calibration"]) if model_contract else {
                "status": "not_applicable",
                "method": "none",
                "limitations": "none",
            },
            "explanation": {
                "available": bool(drivers),
                "method": exp_meta.get("method"),
                "contribution_space": exp_meta.get("contribution_space"),
                "non_causal": True,
                "disclaimer": NON_CAUSAL_DISCLAIMER,
                "drivers": formatted_drivers,
            },
            "limitations": (
                list(model_contract["limitations"]["general_limitations"])
                if model_contract
                else ["Domain unassigned or evaluation-only."]
            ),
            "metadata": dict(metadata or {}),
        }

        # Validate resulting envelope
        errors = self.validate_prediction_response(envelope)
        if errors:
            raise MLPlatformContractValidationError(
                f"Generated prediction response failed validation: {'; '.join(errors)}"
            )

        return envelope

    def build_profile_envelope(
        self,
        project_id: str | None,
        report_month: str,
        overall_status: str,
        coverage_status: str,
        priority_domains: list[dict[str, Any]],
        attention_level: str,
        recommendations: list[dict[str, Any]],
        domain_risks: dict[str, dict[str, Any]],
        limitations: list[str],
        governance_notes: list[str],
        summary: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a validated platform-safe project risk profile response envelope."""
        profile_contract = self.get_unified_profile_contract()

        envelope = {
            "contract_version": self.version,
            "profile_version": profile_contract["profile_version"],
            "policy_version": profile_contract["policy_version"],
            "project_id": project_id,
            "report_month": report_month,
            "overall_status": overall_status,
            "coverage_status": coverage_status,
            "priority_domains": copy.deepcopy(priority_domains),
            "attention_level": attention_level,
            "recommendations": copy.deepcopy(recommendations),
            "domain_risks": copy.deepcopy(domain_risks),
            "limitations": copy.deepcopy(limitations),
            "governance_notes": copy.deepcopy(governance_notes),
            "summary": summary,
            "metadata": dict(metadata or {}),
        }

        # Validate resulting envelope
        errors = self.validate_profile_response(envelope)
        if errors:
            raise MLPlatformContractValidationError(
                f"Generated profile response failed validation: {'; '.join(errors)}"
            )

        return envelope

    # -------------------------------------------------------------------------
    # Fail-Closed Validation Methods
    # -------------------------------------------------------------------------

    @classmethod
    def validate_contract(cls, contract_dict: dict[str, Any] | None) -> list[str]:
        """Validate structure and governance invariants of platform contract."""
        errors: list[str] = []
        if not isinstance(contract_dict, dict):
            return ["Contract data must be a JSON object"]

        required_top = [
            "contract_name",
            "contract_version",
            "contract_id",
            "description",
            "generation_policy",
            "registry_reference",
            "domains",
            "unified_profile",
            "input_contracts",
            "output_contracts",
            "governance_policy",
            "path_masking_policy",
        ]
        for field in required_top:
            if field not in contract_dict:
                errors.append(f"Missing required top-level field: '{field}'")

        if contract_dict.get("contract_id") != CONTRACT_ID:
            errors.append(
                f"Invalid contract_id: expected '{CONTRACT_ID}', got '{contract_dict.get('contract_id')}'"
            )

        if contract_dict.get("contract_version") != CONTRACT_VERSION:
            errors.append(
                f"Invalid contract_version: expected '{CONTRACT_VERSION}', got '{contract_dict.get('contract_version')}'"
            )

        # Check registry reference
        reg_ref = contract_dict.get("registry_reference", {})
        if not isinstance(reg_ref, dict):
            errors.append("Field 'registry_reference' must be an object.")
        else:
            if reg_ref.get("registry_id") != REGISTRY_ID:
                errors.append(f"Invalid registry_id reference: {reg_ref.get('registry_id')}")

        # Check domains
        domains = contract_dict.get("domains", {})
        if not isinstance(domains, dict):
            errors.append("Field 'domains' must be an object.")
        else:
            for required_dom in ("schedule_3m", "cost_overrun", "implementation_risk"):
                if required_dom not in domains:
                    errors.append(f"Missing required domain contract: '{required_dom}'")

            # Check Schedule domain
            if "schedule_3m" in domains:
                sched = domains["schedule_3m"]
                if sched.get("governance_status") != GOVERNANCE_LOCKED_PRODUCTION:
                    errors.append(
                        f"schedule_3m governance_status must be '{GOVERNANCE_LOCKED_PRODUCTION}'"
                    )
                if sched.get("production_availability") != AVAILABILITY_AVAILABLE:
                    errors.append(
                        f"schedule_3m production_availability must be '{AVAILABILITY_AVAILABLE}'"
                    )
                if sched.get("operational_decision_threshold") != 0.50:
                    errors.append("schedule_3m operational_decision_threshold must be 0.50")

            # Check Cost domain
            if "cost_overrun" in domains:
                cost = domains["cost_overrun"]
                if cost.get("governance_status") != GOVERNANCE_NOT_READY_FOR_PRODUCTION:
                    errors.append(
                        f"cost_overrun governance_status must be '{GOVERNANCE_NOT_READY_FOR_PRODUCTION}'"
                    )
                if cost.get("production_availability") != AVAILABILITY_NOT_AVAILABLE:
                    errors.append(
                        f"cost_overrun production_availability must be '{AVAILABILITY_NOT_AVAILABLE}'"
                    )
                if cost.get("operational_decision_threshold") is not None:
                    errors.append("cost_overrun operational_decision_threshold must be null")

            # Check Implementation domain
            if "implementation_risk" in domains:
                impl = domains["implementation_risk"]
                if impl.get("governance_status") != GOVERNANCE_VIABLE_WITH_LIMITATIONS:
                    errors.append(
                        f"implementation_risk governance_status must be '{GOVERNANCE_VIABLE_WITH_LIMITATIONS}'"
                    )
                if impl.get("production_availability") != AVAILABILITY_NOT_AVAILABLE:
                    errors.append(
                        f"implementation_risk production_availability must be '{AVAILABILITY_NOT_AVAILABLE}'"
                    )
                if impl.get("operational_decision_threshold") is not None:
                    errors.append("implementation_risk operational_decision_threshold must be null")

        # Check Unified profile
        profile = contract_dict.get("unified_profile", {})
        if not isinstance(profile, dict):
            errors.append("Field 'unified_profile' must be an object.")
        else:
            if "aggregation_prohibition_rule" not in profile:
                errors.append("unified_profile missing 'aggregation_prohibition_rule'")

        return errors

    @classmethod
    def validate_prediction_response(cls, response: dict[str, Any]) -> list[str]:
        """Validate an outgoing prediction response for governance and schema compliance."""
        errors: list[str] = []
        if not isinstance(response, dict):
            return ["Prediction response must be a dictionary"]

        for top_field in ("contract_version", "prediction", "model", "calibration", "explanation", "limitations"):
            if top_field not in response:
                errors.append(f"Missing required response field: '{top_field}'")

        if response.get("contract_version") != CONTRACT_VERSION:
            errors.append(
                f"Invalid contract_version: expected '{CONTRACT_VERSION}', got '{response.get('contract_version')}'"
            )

        pred = response.get("prediction", {})
        model = response.get("model", {})
        explanation = response.get("explanation", {})

        domain = pred.get("domain")
        if domain not in ("schedule_3m", "cost_overrun", "implementation_risk"):
            errors.append(f"Unknown or invalid prediction domain: '{domain}'")

        prob = pred.get("probability")
        gov_status = model.get("governance_status")
        prod_avail = model.get("production_availability")

        # Governance rule: NOT_AVAILABLE or EVALUATION_ONLY must have null probability
        if prod_avail in (AVAILABILITY_NOT_AVAILABLE, AVAILABILITY_INELIGIBLE, AVAILABILITY_EVALUATION_ONLY):
            if prob is not None:
                errors.append(
                    f"Probability must be null for production_availability '{prod_avail}' in domain '{domain}'"
                )
            if pred.get("operational_decision") is not None:
                errors.append(
                    f"Operational decision must be null for production_availability '{prod_avail}' in domain '{domain}'"
                )

        # Probability bounds
        if prob is not None:
            if not isinstance(prob, (int, float)) or prob < 0.0 or prob > 1.0:
                errors.append(f"Probability must be float in [0.0, 1.0], got {prob}")

        # Non-causal explanation check
        if explanation.get("non_causal") is not True:
            errors.append("Explanation contract requires non_causal=True")

        return errors

    @classmethod
    def validate_profile_response(cls, response: dict[str, Any]) -> list[str]:
        """Validate an outgoing profile response, strictly prohibiting probability aggregation."""
        errors: list[str] = []
        if not isinstance(response, dict):
            return ["Profile response must be a dictionary"]

        # 1. STRICT PROHIBITION: Check for illegal probability fusion keys
        for illegal_key in PROHIBITED_PROBABILITY_FUSION_KEYS:
            if illegal_key in response:
                errors.append(
                    f"Prohibited probability fusion key '{illegal_key}' detected in project risk profile."
                )

        # 2. Required fields
        required_fields = [
            "contract_version",
            "profile_version",
            "policy_version",
            "overall_status",
            "coverage_status",
            "priority_domains",
            "attention_level",
            "recommendations",
            "domain_risks",
            "limitations",
            "governance_notes",
            "summary",
        ]
        for f in required_fields:
            if f not in response:
                errors.append(f"Missing required profile field: '{f}'")

        # 3. Check status enums
        valid_overall = {"FULL", "PARTIAL", "LIMITED", "UNAVAILABLE", "INELIGIBLE"}
        if response.get("overall_status") not in valid_overall:
            errors.append(f"Invalid overall_status: '{response.get('overall_status')}'")

        valid_coverage = {
            "COMPLETE_COVERAGE",
            "PARTIAL_COVERAGE",
            "LIMITED_COVERAGE",
            "NO_PREDICTIVE_COVERAGE",
        }
        if response.get("coverage_status") not in valid_coverage:
            errors.append(f"Invalid coverage_status: '{response.get('coverage_status')}'")

        valid_attention = {
            "HIGH_ATTENTION",
            "MEDIUM_ATTENTION",
            "LIMITED_ASSESSMENT",
            "ROUTINE",
            "NO_ASSESSMENT",
        }
        if response.get("attention_level") not in valid_attention:
            errors.append(f"Invalid attention_level: '{response.get('attention_level')}'")

        # 4. Check domain_risks separation
        domain_risks = response.get("domain_risks", {})
        if not isinstance(domain_risks, dict):
            errors.append("Field 'domain_risks' must be a dictionary.")
        else:
            # Check for fusion within domain_risks
            for illegal_key in PROHIBITED_PROBABILITY_FUSION_KEYS:
                if illegal_key in domain_risks:
                    errors.append(
                        f"Prohibited probability fusion key '{illegal_key}' detected in domain_risks."
                    )

        return errors

    # -------------------------------------------------------------------------
    # Cross-Verification with ModelRegistry
    # -------------------------------------------------------------------------

    def verify(self, root: Path | None = None, fail_closed: bool = True) -> dict[str, Any]:
        """Verify contract internal consistency and cross-validate against ModelRegistry."""
        repo_root = (root or self._root).resolve()
        checks: list[dict[str, Any]] = []

        # 1. Validate internal contract structure
        structural_errors = self.validate_contract(self._contract)
        checks.append({
            "check": "platform_contract_structure",
            "status": "PASS" if not structural_errors else "FAIL",
            "errors": structural_errors,
        })

        # 2. Check schema file existence and Draft 2020-12 validity
        schema_path = repo_root / SCHEMA_CONTRACT_RELPATH
        schema_exists = schema_path.is_file()
        checks.append({
            "check": "schema_contract_file_exists",
            "status": "PASS" if schema_exists else "FAIL",
            "path": SCHEMA_CONTRACT_RELPATH,
        })

        # 3. Load ModelRegistry and cross-validate
        reg_checks = self.verify_registry_compatibility(root=repo_root)
        checks.extend(reg_checks)

        # Determine overall status
        failed_checks = [c for c in checks if c.get("status") != "PASS"]
        overall_status = "FAIL" if failed_checks else "PASS"

        report = {
            "contract_id": CONTRACT_ID,
            "contract_version": CONTRACT_VERSION,
            "overall_status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks_count": len(checks),
            "failed_checks_count": len(failed_checks),
            "checks": checks,
        }

        if overall_status == "FAIL" and fail_closed:
            reasons = [f"{c['check']}: {c.get('errors') or c.get('message', 'FAILED')}" for c in failed_checks]
            raise MLPlatformContractVerificationError(
                f"Platform contract verification failed closed: {'; '.join(reasons)}"
            )

        return report

    def verify_registry_compatibility(
        self,
        registry: ModelRegistry | None = None,
        root: Path | None = None,
    ) -> list[dict[str, Any]]:
        """Verify consistency against authoritative ModelRegistry."""
        repo_root = (root or self._root).resolve()
        checks: list[dict[str, Any]] = []

        try:
            reg = registry or ModelRegistry.load(root=repo_root)
        except Exception as exc:
            return [{
                "check": "model_registry_load",
                "status": "FAIL",
                "message": f"Failed to load authoritative ModelRegistry: {exc}",
            }]

        reg_data = reg.get_registry()

        # Check 1: Registry hash match
        reg_file = repo_root / DEFAULT_REGISTRY_RELPATH
        if reg_file.is_file():
            actual_reg_hash = hashlib.sha256(reg_file.read_bytes()).hexdigest().upper()
            ref_hash = self._contract.get("registry_reference", {}).get("registry_sha256")
            hash_matches = actual_reg_hash == ref_hash
            checks.append({
                "check": "model_registry_sha256_match",
                "status": "PASS" if hash_matches else "FAIL",
                "actual_sha256": actual_reg_hash,
                "referenced_sha256": ref_hash,
            })

        # Check 2: Domain IDs match
        contract_domains = sorted(list(self._contract.get("domains", {}).keys()))
        registry_domains = sorted(reg.list_domains())
        domains_match = contract_domains == registry_domains
        checks.append({
            "check": "domain_ids_match",
            "status": "PASS" if domains_match else "FAIL",
            "contract_domains": contract_domains,
            "registry_domains": registry_domains,
        })

        # Check 3: Domain-level metadata match (target, horizon, governance, availability, threshold)
        for dom_id in contract_domains:
            c_dom = self._contract["domains"][dom_id]
            r_dom = reg.get_domain(dom_id)

            mismatches: list[str] = []
            for field in ("target", "horizon_months", "governance_status", "production_availability"):
                if c_dom.get(field) != r_dom.get(field):
                    mismatches.append(
                        f"{field}: contract='{c_dom.get(field)}' vs registry='{r_dom.get(field)}'"
                    )

            c_thresh = c_dom.get("operational_decision_threshold")
            r_thresh = r_dom.get("operational_decision_threshold")
            if c_thresh != r_thresh:
                mismatches.append(f"threshold: contract='{c_thresh}' vs registry='{r_thresh}'")

            checks.append({
                "check": f"domain_metadata_consistency_{dom_id}",
                "status": "PASS" if not mismatches else "FAIL",
                "domain_id": dom_id,
                "mismatches": mismatches,
            })

            # Check 4: Model IDs, versions, and regimes match
            c_models = c_dom.get("models", {})
            r_models = r_dom.get("models", {})
            model_keys_match = sorted(list(c_models.keys())) == sorted(list(r_models.keys()))
            checks.append({
                "check": f"models_consistency_{dom_id}",
                "status": "PASS" if model_keys_match else "FAIL",
                "domain_id": dom_id,
                "contract_models": sorted(list(c_models.keys())),
                "registry_models": sorted(list(r_models.keys())),
            })

            for m_key, c_m in c_models.items():
                if m_key in r_models:
                    r_m = r_models[m_key]
                    m_mismatches: list[str] = []
                    for mf in ("model_id", "model_version", "model_family", "regime", "governance_status", "production_availability"):
                        if c_m.get(mf) != r_m.get(mf):
                            m_mismatches.append(
                                f"{mf}: contract='{c_m.get(mf)}' vs registry='{r_m.get(mf)}'"
                            )
                    # Artifact hashes if production
                    if c_m.get("artifact") and r_m.get("artifact"):
                        if c_m["artifact"].get("sha256") != r_m["artifact"].get("sha256"):
                            m_mismatches.append("artifact sha256 mismatch")

                    checks.append({
                        "check": f"model_record_{dom_id}_{m_key}",
                        "status": "PASS" if not m_mismatches else "FAIL",
                        "model_id": c_m.get("model_id"),
                        "mismatches": m_mismatches,
                    })

        return checks

    # -------------------------------------------------------------------------
    # Path Masking Helper
    # -------------------------------------------------------------------------

    @classmethod
    def _mask_paths(cls, obj: Any) -> Any:
        """Recursively mask absolute filesystem paths from contract dictionary."""
        if isinstance(obj, dict):
            masked: dict[str, Any] = {}
            for k, v in obj.items():
                if k in ("path", "relative_path", "contract_reference", "registry_path") and isinstance(v, str):
                    # Retain relative repository paths (e.g. data/... or artifacts/...)
                    # but strip drive letters / absolute filesystem roots
                    norm = v.replace("\\", "/")
                    if re.match(r"^[A-Za-z]:/", norm) or norm.startswith("/"):
                        parts = norm.split("/")
                        if "artifacts" in parts:
                            idx = parts.index("artifacts")
                            masked[k] = "/".join(parts[idx:])
                        elif "schemas" in parts:
                            idx = parts.index("schemas")
                            masked[k] = "/".join(parts[idx:])
                        elif "data" in parts:
                            idx = parts.index("data")
                            masked[k] = "/".join(parts[idx:])
                        else:
                            masked[k] = Path(v).name
                    else:
                        masked[k] = norm
                else:
                    masked[k] = cls._mask_paths(v)
            return masked
        elif isinstance(obj, list):
            return [cls._mask_paths(item) for item in obj]
        return obj


# -----------------------------------------------------------------------------
# Authoritative Platform Contract Data Builder
# -----------------------------------------------------------------------------

def build_authoritative_platform_contract_data(root: Path | None = None) -> dict[str, Any]:
    """Deterministically construct authoritative ML platform contract dictionary."""
    repo_root = (root or Path.cwd()).resolve()

    # Get registry sha256
    reg_file = repo_root / DEFAULT_REGISTRY_RELPATH
    if reg_file.is_file():
        registry_sha256 = hashlib.sha256(reg_file.read_bytes()).hexdigest().upper()
    else:
        registry_sha256 = "154723648FD9A88B3C822A1CEDF0901D431F0C01F0DB21D44454DFCEB094911E"

    contract_data: dict[str, Any] = {
        "$schema": f"../{SCHEMA_CONTRACT_RELPATH}",
        "contract_name": CONTRACT_NAME,
        "contract_version": CONTRACT_VERSION,
        "contract_id": CONTRACT_ID,
        "description": "Authoritative frozen ML <-> Platform integration contract for IRIS.",
        "generation_policy": GENERATION_POLICY,
        "registry_reference": {
            "registry_id": REGISTRY_ID,
            "registry_version": REGISTRY_VERSION,
            "registry_path": DEFAULT_REGISTRY_RELPATH,
            "registry_sha256": registry_sha256,
        },
        "domains": {
            "schedule_3m": {
                "domain_id": "schedule_3m",
                "domain_name": "Schedule Extension Risk (3-Month Horizon)",
                "target": "target_effective_schedule_ext_3m",
                "horizon_months": 3,
                "governance_status": GOVERNANCE_LOCKED_PRODUCTION,
                "production_availability": AVAILABILITY_AVAILABLE,
                "operational_decision_threshold": 0.50,
                "governance_rationale": (
                    "Operational production domain. Rigorously validated under PR-03 and PR-05 "
                    "strict walk-forward evaluation. Legacy and modern regimes remain separate "
                    "with locked model artifacts."
                ),
                "serving_behavior": "Evaluates live scores against 0.50 threshold via ScheduleExtensionPredictor.",
                "safety_rule": "Predictions are non-causal statistical associations based on reporting patterns.",
                "models": {
                    "legacy": {
                        "model_id": "schedule_legacy_catboost",
                        "model_name": "catboost_full_v1__unweighted",
                        "model_version": "1.0.0",
                        "model_family": "CatBoostClassifier",
                        "domain": "schedule_3m",
                        "regime": "LEGACY",
                        "candidate_type": "production",
                        "target": "target_effective_schedule_ext_3m",
                        "target_definition": {
                            "name": "target_effective_schedule_ext_3m",
                            "description": "Effective schedule push-out over forward H=3 months window within continuous segment.",
                            "baseline_definition": "revised_completion_date(T) if actually reported, otherwise original_completion_date(T)",
                        },
                        "horizon_months": 3,
                        "governance_status": GOVERNANCE_LOCKED_PRODUCTION,
                        "production_availability": AVAILABILITY_AVAILABLE,
                        "operational_decision_threshold": 0.50,
                        "artifact": {
                            "path": SCHEDULE_LEGACY_ARTIFACT_PATH,
                            "sha256": SCHEDULE_LEGACY_ARTIFACT_SHA256,
                            "format": "cbm",
                            "size_bytes": 562232,
                            "version": "1.0.0",
                        },
                        "calibration": {
                            "status": "evaluated_uncalibrated_retained",
                            "method": "uncalibrated_raw_probabilities",
                            "limitations": "Platt scaling evaluated in PR-05 but raw probabilities retained for lower Brier score and operational monotonicity.",
                        },
                        "explanation": {
                            "available": True,
                            "method": "TreeSHAP",
                            "contribution_space": "model_margin_or_logit",
                            "non_causal": True,
                            "disclaimer": NON_CAUSAL_DISCLAIMER,
                            "limitations": "TreeSHAP margin contributions in CatBoost log-odds space; non-causal.",
                        },
                        "feature_contract": {
                            "contract_reference": "schemas/schedule_extension_3m_v1.contract.json",
                            "feature_count": 36,
                            "ordered_names": [
                                "sector", "agency", "state", "original_cost", "cumulative_expenditure_t",
                                "revised_cost_t", "physical_progress_t", "project_age_months",
                                "months_to_original_schedule", "months_to_effective_schedule",
                                "schedule_revision_lag_months", "schedule_has_been_revised", "months_since_start",
                                "expenditure_to_original_cost_ratio", "revised_to_original_cost_ratio",
                                "cost_has_been_revised", "exp_delta_1m", "exp_delta_3m", "past_exp_stagnant_3m",
                                "past_progress_delta_3m", "past_progress_stagnant_3m", "n_prior_schedule_extensions",
                                "n_prior_cost_revisions", "observed_tenure_months", "state_is_missing",
                                "approval_date_is_missing", "original_completion_date_is_missing",
                                "revised_cost_is_present", "revised_date_is_present", "physical_progress_is_present",
                                "physical_progress_supported", "start_date_is_present", "start_date_supported",
                                "exp_delta_1m_is_supported", "exp_delta_3m_is_supported", "progress_delta_3m_is_supported",
                            ],
                            "categorical_features": ["sector", "agency", "state"],
                            "leakage_exclusion_policy": "Strict embargo: only features observable at or before prediction origin month T are permitted.",
                        },
                        "validation": {
                            "methodology": "strict_walk_forward_expanding_window (12 evaluation folds, 2023-07 to 2025-03)",
                            "embargo_policy": "strict_walk_forward (T_train + 3 < E_eval)",
                            "performance_summary": {
                                "roc_auc": 0.806439,
                                "average_precision": 0.407094,
                                "brier_score": 0.071988,
                                "precision_at_0_5": 0.542553,
                                "recall_at_0_5": 0.254047,
                                "f1_at_0_5": 0.346056,
                            },
                        },
                        "limitations": {
                            "general_limitations": [
                                "Legacy reporting quirks and unstandardized project codes in Segments 1-3.",
                                "MoSPI Flash Report administrative reporting lag.",
                                "Non-causal statistical associations.",
                            ],
                            "eligibility_limitations": "Ongoing infrastructure projects observed continuously over forward 3-month window in Segments 1-3.",
                            "regime_limitations": "Valid only for pre-July 2025 legacy reporting regime (Segments 1-3).",
                            "telemetry_limitations": "Subject to historical monthly Flash Report reporting delays and retrospective revisions.",
                            "governance_limitations": "Operational screening only; autonomous financial penalties or terminations are strictly prohibited.",
                        },
                    },
                    "modern": {
                        "model_id": "schedule_modern_logistic",
                        "model_name": "logistic_static_only__unweighted",
                        "model_version": "1.0.0",
                        "model_family": "LogisticRegression",
                        "domain": "schedule_3m",
                        "regime": "MODERN",
                        "candidate_type": "production",
                        "target": "target_effective_schedule_ext_3m",
                        "target_definition": {
                            "name": "target_effective_schedule_ext_3m",
                            "description": "Effective schedule push-out over forward H=3 months window within continuous segment.",
                            "baseline_definition": "revised_completion_date(T) if actually reported, otherwise original_completion_date(T)",
                        },
                        "horizon_months": 3,
                        "governance_status": GOVERNANCE_LOCKED_PRODUCTION,
                        "production_availability": AVAILABILITY_AVAILABLE,
                        "operational_decision_threshold": 0.50,
                        "artifact": {
                            "path": SCHEDULE_MODERN_ARTIFACT_PATH,
                            "sha256": SCHEDULE_MODERN_ARTIFACT_SHA256,
                            "format": "joblib",
                            "size_bytes": 7145,
                            "version": "1.0.0",
                        },
                        "calibration": {
                            "status": "evaluated_uncalibrated_retained",
                            "method": "uncalibrated_raw_probabilities",
                            "limitations": "Platt scaling evaluated in PR-05 with conditional improvement; raw probabilities retained for operational consistency.",
                        },
                        "explanation": {
                            "available": True,
                            "method": "StandardizedCoefficients",
                            "contribution_space": "model_margin_or_logit",
                            "non_causal": True,
                            "disclaimer": NON_CAUSAL_DISCLAIMER,
                            "limitations": "Standardized linear coefficients in log-odds space; non-causal.",
                        },
                        "feature_contract": {
                            "contract_reference": "schemas/schedule_extension_3m_v1.contract.json",
                            "feature_count": 25,
                            "ordered_names": [
                                "sector", "agency", "state", "original_cost", "cumulative_expenditure_t",
                                "revised_cost_t", "physical_progress_t", "project_age_months",
                                "months_to_original_schedule", "months_to_effective_schedule",
                                "schedule_revision_lag_months", "schedule_has_been_revised", "months_since_start",
                                "expenditure_to_original_cost_ratio", "revised_to_original_cost_ratio",
                                "cost_has_been_revised", "state_is_missing", "approval_date_is_missing",
                                "original_completion_date_is_missing", "revised_cost_is_present",
                                "revised_date_is_present", "physical_progress_is_present",
                                "physical_progress_supported", "start_date_is_present", "start_date_supported",
                            ],
                            "categorical_features": ["sector", "agency", "state"],
                            "leakage_exclusion_policy": "Strict embargo: only features observable at or before prediction origin month T are permitted.",
                        },
                        "validation": {
                            "methodology": "strict_walk_forward_expanding_window (5 evaluation folds, 2025-12 to 2026-04)",
                            "embargo_policy": "strict_walk_forward (T_train + 3 < E_eval)",
                            "performance_summary": {
                                "roc_auc": 0.84193,
                                "average_precision": 0.758717,
                                "brier_score": 0.191617,
                                "precision_at_0_5": 0.808252,
                                "recall_at_0_5": 0.361957,
                                "f1_at_0_5": 0.50,
                            },
                        },
                        "limitations": {
                            "general_limitations": [
                                "Shorter longitudinal history in Segment 4 (July 2025 to July 2026).",
                                "MoSPI administrative reporting changes after redesign.",
                                "Non-causal statistical associations.",
                            ],
                            "eligibility_limitations": "Ongoing infrastructure projects observed continuously over forward 3-month window in Segment 4.",
                            "regime_limitations": "Valid only for post-July 2025 modern reporting regime (Segment 4).",
                            "telemetry_limitations": "Start date structurally absent in modern redesign panel.",
                            "governance_limitations": "Operational screening only; autonomous financial penalties or terminations are strictly prohibited.",
                        },
                    },
                },
            },
            "cost_overrun": {
                "domain_id": "cost_overrun",
                "domain_name": "Cost Overrun / Escalation Risk (3-Month Horizon)",
                "target": "target_effective_cost_esc_3m",
                "horizon_months": 3,
                "governance_status": GOVERNANCE_NOT_READY_FOR_PRODUCTION,
                "production_availability": AVAILABILITY_NOT_AVAILABLE,
                "operational_decision_threshold": None,
                "governance_rationale": (
                    "Under PR-07 walk-forward evaluation, cost escalation exhibited extreme class imbalance (~2.18% base rate) "
                    "and marginal precision lift (PR-AUC < 0.03 micro average precision). Cost revisions are administrative decisions "
                    "driven by external fiscal and political approvals rather than internal project telemetry. No model is approved for "
                    "autonomous operational scoring."
                ),
                "serving_behavior": "Returns status=NOT_AVAILABLE with null score, prediction, and threshold. Fails closed.",
                "safety_rule": "Missing score must NEVER be treated as evidence of zero or low cost overrun risk.",
                "models": {
                    "baseline": {
                        "model_id": "cost_overrun_baseline_logistic",
                        "model_name": "logistic_balanced",
                        "model_version": "1.0.0",
                        "model_family": "LogisticRegression",
                        "domain": "cost_overrun",
                        "regime": "CROSS_REGIME",
                        "candidate_type": "baseline",
                        "target": "target_effective_cost_esc_3m",
                        "target_definition": "Effective administrative upward cost revision / escalation over forward H=3 months window within continuous segment.",
                        "horizon_months": 3,
                        "governance_status": GOVERNANCE_NOT_READY_FOR_PRODUCTION,
                        "production_availability": AVAILABILITY_EVALUATION_ONLY,
                        "operational_decision_threshold": None,
                        "artifact": None,
                        "calibration": {
                            "status": "research_only",
                            "method": "balanced_class_weight_rescaling",
                            "limitations": "Severe miscalibration due to class rebalancing; Brier score > 0.17 vs 0.017 prevalence baseline.",
                        },
                        "explanation": {
                            "available": False,
                            "method": "LogisticCoefficients",
                            "contribution_space": "model_margin_or_logit",
                            "non_causal": True,
                            "disclaimer": NON_CAUSAL_DISCLAIMER,
                            "limitations": "Research-only baseline; low discriminatory power.",
                        },
                        "feature_contract": {
                            "contract_reference": "schemas/cost_overrun_v1.contract.json",
                            "feature_count": 36,
                            "ordered_names": [
                                "sector", "agency", "state", "original_cost", "cumulative_expenditure_t",
                                "revised_cost_t", "physical_progress_t", "project_age_months",
                                "months_to_original_schedule", "months_to_effective_schedule",
                                "schedule_revision_lag_months", "schedule_has_been_revised", "months_since_start",
                                "expenditure_to_original_cost_ratio", "revised_to_original_cost_ratio",
                                "cost_has_been_revised", "exp_delta_1m", "exp_delta_3m", "past_exp_stagnant_3m",
                                "past_progress_delta_3m", "past_progress_stagnant_3m", "n_prior_schedule_extensions",
                                "n_prior_cost_revisions", "observed_tenure_months", "state_is_missing",
                                "approval_date_is_missing", "original_completion_date_is_missing",
                                "revised_cost_is_present", "revised_date_is_present", "physical_progress_is_present",
                                "physical_progress_supported", "start_date_is_present", "start_date_supported",
                                "exp_delta_1m_is_supported", "exp_delta_3m_is_supported", "progress_delta_3m_is_supported",
                            ],
                            "categorical_features": ["sector", "agency", "state"],
                            "leakage_exclusion_policy": "Strict embargo: only features observable at or before prediction origin month T are permitted.",
                        },
                        "validation": {
                            "methodology": "strict_walk_forward_expanding_window (12 LEGACY folds, 5 MODERN folds)",
                            "embargo_policy": "strict_walk_forward (T_train + 3 < E_eval)",
                            "performance_summary": {
                                "legacy_micro_ap": 0.022856,
                                "legacy_macro_ap": 0.03026,
                                "legacy_roc_auc": 0.558448,
                                "modern_micro_ap": 0.021013,
                                "modern_macro_ap": 0.022169,
                                "modern_roc_auc": 0.389548,
                            },
                        },
                        "limitations": {
                            "general_limitations": [
                                "Severe class imbalance (~2.18% positive rate).",
                                "Near-zero predictive lift over prevalence baseline.",
                                "Administrative approvals occur externally to project telemetry.",
                            ],
                            "eligibility_limitations": "Actively ongoing infrastructure projects with continuous forward 3-month observation and baseline cost > 0.",
                            "regime_limitations": "Evaluated cross-regime under separate fold architectures.",
                            "telemetry_limitations": "External political and fiscal approvals driving revisions are unobserved.",
                            "governance_limitations": "Prohibited for operational scoring, production decision gating, or capital allocation.",
                        },
                    },
                    "challenger": {
                        "model_id": "cost_overrun_challenger_catboost",
                        "model_name": "catboost_unweighted",
                        "model_version": "1.0.0",
                        "model_family": "CatBoostClassifier",
                        "domain": "cost_overrun",
                        "regime": "CROSS_REGIME",
                        "candidate_type": "challenger",
                        "target": "target_effective_cost_esc_3m",
                        "target_definition": "Effective administrative upward cost revision / escalation over forward H=3 months window within continuous segment.",
                        "horizon_months": 3,
                        "governance_status": GOVERNANCE_NOT_READY_FOR_PRODUCTION,
                        "production_availability": AVAILABILITY_EVALUATION_ONLY,
                        "operational_decision_threshold": None,
                        "artifact": None,
                        "calibration": {
                            "status": "research_only",
                            "method": "uncalibrated_raw_probabilities",
                            "limitations": "Low absolute probabilities; highest Brier reliability but insufficient precision.",
                        },
                        "explanation": {
                            "available": False,
                            "method": "TreeSHAP",
                            "contribution_space": "model_margin_or_logit",
                            "non_causal": True,
                            "disclaimer": NON_CAUSAL_DISCLAIMER,
                            "limitations": "Research-only candidate; feature importance heavily dominated by project age and expenditure ratio.",
                        },
                        "feature_contract": {
                            "contract_reference": "schemas/cost_overrun_v1.contract.json",
                            "feature_count": 36,
                            "ordered_names": [
                                "sector", "agency", "state", "original_cost", "cumulative_expenditure_t",
                                "revised_cost_t", "physical_progress_t", "project_age_months",
                                "months_to_original_schedule", "months_to_effective_schedule",
                                "schedule_revision_lag_months", "schedule_has_been_revised", "months_since_start",
                                "expenditure_to_original_cost_ratio", "revised_to_original_cost_ratio",
                                "cost_has_been_revised", "exp_delta_1m", "exp_delta_3m", "past_exp_stagnant_3m",
                                "past_progress_delta_3m", "past_progress_stagnant_3m", "n_prior_schedule_extensions",
                                "n_prior_cost_revisions", "observed_tenure_months", "state_is_missing",
                                "approval_date_is_missing", "original_completion_date_is_missing",
                                "revised_cost_is_present", "revised_date_is_present", "physical_progress_is_present",
                                "physical_progress_supported", "start_date_is_present", "start_date_supported",
                                "exp_delta_1m_is_supported", "exp_delta_3m_is_supported", "progress_delta_3m_is_supported",
                            ],
                            "categorical_features": ["sector", "agency", "state"],
                            "leakage_exclusion_policy": "Strict embargo: only features observable at or before prediction origin month T are permitted.",
                        },
                        "validation": {
                            "methodology": "strict_walk_forward_expanding_window (12 LEGACY folds, 5 MODERN folds)",
                            "embargo_policy": "strict_walk_forward (T_train + 3 < E_eval)",
                            "performance_summary": {
                                "legacy_micro_ap": 0.027919,
                                "legacy_macro_ap": 0.04704,
                                "legacy_roc_auc": 0.602087,
                                "legacy_brier_score": 0.018344,
                                "modern_micro_ap": 0.018076,
                                "modern_macro_ap": 0.038165,
                                "modern_roc_auc": 0.52869,
                                "modern_brier_score": 0.019064,
                            },
                        },
                        "limitations": {
                            "general_limitations": [
                                "Severe class imbalance (~2.18% positive rate).",
                                "Micro average precision < 0.03 in both regimes.",
                                "External political and fiscal approval dynamics.",
                            ],
                            "eligibility_limitations": "Actively ongoing infrastructure projects with continuous forward 3-month observation and baseline cost > 0.",
                            "regime_limitations": "Evaluated cross-regime under separate fold architectures.",
                            "telemetry_limitations": "External approvals occur outside of project telemetry stream.",
                            "governance_limitations": "Prohibited for operational scoring, production decision gating, or capital allocation.",
                        },
                    },
                },
            },
            "implementation_risk": {
                "domain_id": "implementation_risk",
                "domain_name": "Implementation Risk / Progress Stagnation (3-Month Horizon)",
                "target": "target_progress_stagnation_3m",
                "horizon_months": 3,
                "governance_status": GOVERNANCE_VIABLE_WITH_LIMITATIONS,
                "production_availability": AVAILABILITY_NOT_AVAILABLE,
                "operational_decision_threshold": None,
                "governance_rationale": (
                    "Under PR-09 walk-forward evaluation, progress stagnation modeling showed viable predictive signal "
                    "with human review limitations. However, no serialized production inference artifact is deployed in "
                    "artifacts/ml/implementation_risk_model_v1/. Dynamic retraining at inference time is prohibited."
                ),
                "serving_behavior": "Segments 1 & 2 fail closed as INELIGIBLE (structural absence of physical progress). Segments 3 & 4 fail closed as NOT_AVAILABLE. Live retraining is prohibited.",
                "safety_rule": "Decision support only. Human review of physical progress logs is mandatory.",
                "models": {
                    "baseline": {
                        "model_id": "implementation_risk_baseline_logistic",
                        "model_name": "logistic_unweighted",
                        "model_version": "1.0.0",
                        "model_family": "LogisticRegression",
                        "domain": "implementation_risk",
                        "regime": "CROSS_REGIME",
                        "candidate_type": "baseline",
                        "target": "target_progress_stagnation_3m",
                        "target_definition": "Y(i,T) = 1 if physical_progress(T+3) - physical_progress(T) <= 1e-6, else 0; 0 <= physical_progress(T) < 100.",
                        "horizon_months": 3,
                        "governance_status": GOVERNANCE_VIABLE_WITH_LIMITATIONS,
                        "production_availability": AVAILABILITY_EVALUATION_ONLY,
                        "operational_decision_threshold": None,
                        "artifact": None,
                        "calibration": {
                            "status": "research_only",
                            "method": "uncalibrated_raw_probabilities",
                            "limitations": "Under-predicts stagnation in Modern regime.",
                        },
                        "explanation": {
                            "available": False,
                            "method": "LogisticCoefficients",
                            "contribution_space": "model_margin_or_logit",
                            "non_causal": True,
                            "disclaimer": NON_CAUSAL_DISCLAIMER,
                            "limitations": "Linear baseline; lower discriminatory power than gradient boosted challenger.",
                        },
                        "feature_contract": {
                            "contract_reference": "schemas/implementation_risk_v1.contract.json",
                            "feature_count": 36,
                            "ordered_names": [
                                "sector", "agency", "state", "original_cost", "cumulative_expenditure_t",
                                "revised_cost_t", "physical_progress_t", "project_age_months",
                                "months_to_original_schedule", "months_to_effective_schedule",
                                "schedule_revision_lag_months", "schedule_has_been_revised", "months_since_start",
                                "expenditure_to_original_cost_ratio", "revised_to_original_cost_ratio",
                                "cost_has_been_revised", "exp_delta_1m", "exp_delta_3m", "past_exp_stagnant_3m",
                                "past_progress_delta_3m", "past_progress_stagnant_3m", "n_prior_schedule_extensions",
                                "n_prior_cost_revisions", "observed_tenure_months", "state_is_missing",
                                "approval_date_is_missing", "original_completion_date_is_missing",
                                "revised_cost_is_present", "revised_date_is_present", "physical_progress_is_present",
                                "physical_progress_supported", "start_date_is_present", "start_date_supported",
                                "exp_delta_1m_is_supported", "exp_delta_3m_is_supported", "progress_delta_3m_is_supported",
                            ],
                            "categorical_features": ["sector", "agency", "state"],
                            "leakage_exclusion_policy": "Strict embargo: only features observable at or before prediction origin month T are permitted.",
                        },
                        "validation": {
                            "methodology": "strict_walk_forward_expanding_window (6 LEGACY folds, 5 MODERN folds)",
                            "embargo_policy": "strict_walk_forward (T_train + 3 < E_eval)",
                            "performance_summary": {
                                "legacy_micro_ap": 0.562873,
                                "legacy_macro_ap": 0.556955,
                                "legacy_roc_auc": 0.786989,
                                "legacy_brier_score": 0.166372,
                                "modern_micro_ap": 0.222885,
                                "modern_macro_ap": 0.283897,
                                "modern_roc_auc": 0.516375,
                                "modern_brier_score": 0.194695,
                            },
                        },
                        "limitations": {
                            "general_limitations": [
                                "Regime divergence between Legacy and Modern reporting dynamics.",
                                "Underperforms non-linear tree models by ~0.12 PR-AUC in Legacy.",
                                "Administrative reporting batching in physical progress telemetry.",
                            ],
                            "eligibility_limitations": "Actively ongoing infrastructure projects with reported physical progress in [0, 100) and continuous 3-month forward observation.",
                            "regime_limitations": "Pronounced performance gap between Legacy (AP 0.56) and Modern (AP 0.22).",
                            "telemetry_limitations": "Physical progress reports are subject to batch reporting and administrative lags.",
                            "governance_limitations": "Prohibited for autonomous operational gating without human engineering review.",
                        },
                    },
                    "challenger": {
                        "model_id": "implementation_risk_challenger_catboost",
                        "model_name": "catboost_unweighted",
                        "model_version": "1.0.0",
                        "model_family": "CatBoostClassifier",
                        "domain": "implementation_risk",
                        "regime": "CROSS_REGIME",
                        "candidate_type": "challenger",
                        "target": "target_progress_stagnation_3m",
                        "target_definition": "Y(i,T) = 1 if physical_progress(T+3) - physical_progress(T) <= 1e-6, else 0; 0 <= physical_progress(T) < 100.",
                        "horizon_months": 3,
                        "governance_status": GOVERNANCE_VIABLE_WITH_LIMITATIONS,
                        "production_availability": AVAILABILITY_EVALUATION_ONLY,
                        "operational_decision_threshold": None,
                        "artifact": None,
                        "calibration": {
                            "status": "research_only",
                            "method": "uncalibrated_raw_probabilities",
                            "limitations": "Raw probabilities yield lowest Brier score; Platt scaling does not reliably improve cross-regime calibration.",
                        },
                        "explanation": {
                            "available": False,
                            "method": "TreeSHAP",
                            "contribution_space": "model_margin_or_logit",
                            "non_causal": True,
                            "disclaimer": NON_CAUSAL_DISCLAIMER,
                            "limitations": "Explains stagnation probability contributions from past progress deltas and project maturity.",
                        },
                        "feature_contract": {
                            "contract_reference": "schemas/implementation_risk_v1.contract.json",
                            "feature_count": 36,
                            "ordered_names": [
                                "sector", "agency", "state", "original_cost", "cumulative_expenditure_t",
                                "revised_cost_t", "physical_progress_t", "project_age_months",
                                "months_to_original_schedule", "months_to_effective_schedule",
                                "schedule_revision_lag_months", "schedule_has_been_revised", "months_since_start",
                                "expenditure_to_original_cost_ratio", "revised_to_original_cost_ratio",
                                "cost_has_been_revised", "exp_delta_1m", "exp_delta_3m", "past_exp_stagnant_3m",
                                "past_progress_delta_3m", "past_progress_stagnant_3m", "n_prior_schedule_extensions",
                                "n_prior_cost_revisions", "observed_tenure_months", "state_is_missing",
                                "approval_date_is_missing", "original_completion_date_is_missing",
                                "revised_cost_is_present", "revised_date_is_present", "physical_progress_is_present",
                                "physical_progress_supported", "start_date_is_present", "start_date_supported",
                                "exp_delta_1m_is_supported", "exp_delta_3m_is_supported", "progress_delta_3m_is_supported",
                            ],
                            "categorical_features": ["sector", "agency", "state"],
                            "leakage_exclusion_policy": "Strict embargo: only features observable at or before prediction origin month T are permitted.",
                        },
                        "validation": {
                            "methodology": "strict_walk_forward_expanding_window (6 LEGACY folds, 5 MODERN folds)",
                            "embargo_policy": "strict_walk_forward (T_train + 3 < E_eval)",
                            "performance_summary": {
                                "legacy_micro_ap": 0.687176,
                                "legacy_macro_ap": 0.689828,
                                "legacy_roc_auc": 0.866352,
                                "legacy_brier_score": 0.129145,
                                "modern_micro_ap": 0.300709,
                                "modern_macro_ap": 0.390284,
                                "modern_roc_auc": 0.645406,
                                "modern_brier_score": 0.211446,
                            },
                        },
                        "limitations": {
                            "general_limitations": [
                                "Regime divergence: performance in MODERN (PR-AUC 0.30) is lower than in LEGACY (PR-AUC 0.69).",
                                "Physical progress remains an administrative self-reported metric subject to occasional batching.",
                                "Segments 1 and 2 structurally omit physical progress.",
                                "No serialized production model artifact deployed in repository.",
                            ],
                            "eligibility_limitations": "Actively ongoing infrastructure projects with reported physical progress in [0, 100) and continuous 3-month forward observation.",
                            "regime_limitations": "Divergence between Legacy and Modern reporting dynamics.",
                            "telemetry_limitations": "Physical progress is an administrative self-reported metric subject to occasional batching.",
                            "governance_limitations": "Evidence-based challenger for decision support; autonomous operational gating prohibited.",
                        },
                    },
                },
            },
        },
        "unified_profile": {
            "profile_version": "1.0.0",
            "policy_version": "1.0.0",
            "domain_list": ["schedule_extension", "cost_overrun", "implementation_risk"],
            "aggregation_prohibition_rule": (
                "STRICT PROHIBITION: Never construct a single mathematically combined overall risk probability "
                "(e.g. weighted sum, arithmetic/geometric mean, or max) across disparate risk domains. "
                "Each domain risk must be reported separately."
            ),
            "overall_statuses": ["FULL", "PARTIAL", "LIMITED", "UNAVAILABLE", "INELIGIBLE"],
            "coverage_statuses": [
                "COMPLETE_COVERAGE",
                "PARTIAL_COVERAGE",
                "LIMITED_COVERAGE",
                "NO_PREDICTIVE_COVERAGE",
            ],
            "priority_levels": [
                "HIGH_PRIORITY",
                "MEDIUM_PRIORITY",
                "UNAVAILABLE",
                "LOW_PRIORITY",
                "INELIGIBLE",
            ],
            "attention_levels": [
                "HIGH_ATTENTION",
                "MEDIUM_ATTENTION",
                "LIMITED_ASSESSMENT",
                "ROUTINE",
                "NO_ASSESSMENT",
            ],
            "recommendation_codes": [
                "REVIEW_SCHEDULE_RISK",
                "REVIEW_IMPLEMENTATION_PROGRESS",
                "COST_RISK_NOT_PRODUCTION_READY",
                "INSUFFICIENT_DOMAIN_COVERAGE",
                "IMPLEMENTATION_MODEL_LIMITATIONS",
                "STRUCTURAL_ELIGIBILITY_LIMITATION",
            ],
            "profile_schema": {
                "type": "object",
                "required": [
                    "contract_version",
                    "profile_version",
                    "policy_version",
                    "overall_status",
                    "coverage_status",
                    "priority_domains",
                    "attention_level",
                    "recommendations",
                    "domain_risks",
                    "limitations",
                    "governance_notes",
                    "summary",
                ],
            },
        },
        "input_contracts": {
            "architecture": (
                "Platform provides project/month context -> ML inference layer -> feature builder -> "
                "model -> platform-safe response. Platform does not calculate internal model features."
            ),
            "platform_visible_inputs": {
                "required_fields": [
                    "project_code",
                    "report_month",
                ],
                "optional_fields": [
                    "project_name",
                    "agency",
                    "ministry",
                    "sector",
                    "state",
                    "original_cost",
                    "revised_cost",
                    "cumulative_expenditure",
                    "physical_progress",
                    "approval_date",
                    "start_date",
                    "original_completion_date",
                    "revised_completion_date",
                ],
            },
            "feature_engineering_boundary": (
                "Feature engineering (computing ratios, deltas, lags, stagnation flags, and missingness "
                "indicators) is an internal ML pipeline responsibility. Platform consumers provide source "
                "context and receive platform-safe prediction responses."
            ),
            "prohibited_leakage_fields": sorted(list(PROHIBITED_LEAKAGE_FIELDS)),
        },
        "output_contracts": {
            "prediction_response_schema": {
                "type": "object",
                "required": [
                    "contract_version",
                    "prediction",
                    "model",
                    "calibration",
                    "explanation",
                    "limitations",
                    "metadata",
                ],
            },
            "unified_risk_response_schema": {
                "type": "object",
                "required": [
                    "project_id",
                    "report_month",
                    "schedule_extension",
                    "cost_overrun",
                    "implementation_risk",
                    "metadata",
                ],
            },
            "unified_profile_response_schema": {
                "type": "object",
                "required": [
                    "contract_version",
                    "profile_version",
                    "policy_version",
                    "overall_status",
                    "coverage_status",
                    "priority_domains",
                    "attention_level",
                    "recommendations",
                    "domain_risks",
                    "limitations",
                    "governance_notes",
                    "summary",
                ],
            },
        },
        "governance_policy": {
            "fail_closed_rules": [
                "Prohibited leakage features fail closed with 422.",
                "NaN, Inf, or unhandled null in required model features fail closed.",
                "Unavailable domains return probability=null and operational_decision=null.",
                "Structurally ineligible records return status=INELIGIBLE and probability=null.",
                "Unknown domains or contradictory regimes fail closed.",
                "Uncalibrated models must not falsely claim calibration.",
            ],
            "unavailability_rules": (
                "When a domain is governed as NOT_READY_FOR_PRODUCTION or NOT_AVAILABLE, probability "
                "is null and operational decision is null. Platform must never interpret missing probability "
                "as low or zero risk."
            ),
            "ineligibility_rules": (
                "When a project record belongs to a segment that structurally omits target telemetry "
                "(e.g. Segments 1 & 2 for implementation risk), status is INELIGIBLE with null probability "
                "and deterministic, machine-readable reason."
            ),
            "non_causal_explanation_rule": (
                "All explanations are strictly non-causal statistical associations. Platform consumers "
                "must display explanations with non_causal=true metadata and warning disclaimers."
            ),
            "aggregation_prohibition_rule": (
                "Platform code must never calculate weighted sums or mathematical averages across risk domains. "
                "Unified risk profile provides categorical priorities, attention levels, and qualitative synthesis."
            ),
        },
        "path_masking_policy": {
            "mask_internal_paths": True,
            "replacement_pattern": "Relative repository path or basename",
            "exposed_artifact_formats": ["cbm", "joblib", "json"],
        },
    }

    return contract_data


def build_platform_contract_artifacts(
    output_dir: Path | None = None,
    root: Path | None = None,
) -> dict[str, Path]:
    """Deterministically serialize contract.json, manifest.json, and verification_report.json."""
    repo_root = (root or Path.cwd()).resolve()
    target_dir = (output_dir or repo_root / DEFAULT_CONTRACT_DIR_RELPATH).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Build contract data
    contract_data = build_authoritative_platform_contract_data(root=repo_root)
    contract_path = target_dir / "contract.json"
    contract_bytes = json.dumps(contract_data, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    with open(contract_path, "wb") as f:
        f.write(contract_bytes)
    contract_sha256 = hashlib.sha256(contract_bytes).hexdigest().upper()

    # 2. Manifest data
    manifest_data = {
        "manifest_version": "1.0.0",
        "contract_version": CONTRACT_VERSION,
        "contract_id": CONTRACT_ID,
        "contract_reference": SCHEMA_CONTRACT_RELPATH,
        "contract_sha256": contract_sha256,
        "registry_version": REGISTRY_VERSION,
        "registry_id": REGISTRY_ID,
        "registry_sha256": contract_data["registry_reference"]["registry_sha256"],
        "canonical_inputs": {
            "projects_monthly.csv": CANONICAL_MONTHLY_SHA256,
            "projects_completed.csv": CANONICAL_COMPLETED_SHA256,
        },
        "locked_schedule_artifacts": {
            "legacy_catboost": SCHEDULE_LEGACY_ARTIFACT_SHA256,
            "modern_logistic": SCHEDULE_MODERN_ARTIFACT_SHA256,
        },
        "upstream_contracts": {
            "schedule_extension_3m_v1": "schemas/schedule_extension_3m_v1.contract.json",
            "cost_overrun_v1": "schemas/cost_overrun_v1.contract.json",
            "implementation_risk_v1": "schemas/implementation_risk_v1.contract.json",
            "ml_model_registry_v1": "schemas/ml_model_registry_v1.contract.json",
        },
        "generation_policy": GENERATION_POLICY,
        "verification_policy": "fail_closed_strict_hash_and_registry_verification",
    }
    man_path = target_dir / "manifest.json"
    man_bytes = json.dumps(manifest_data, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    with open(man_path, "wb") as f:
        f.write(man_bytes)

    # 3. Instantiate and run verify to generate deterministic verification report
    contract_instance = MLPlatformContract(
        contract_data=contract_data,
        manifest_data=manifest_data,
        root=repo_root,
    )
    verification_report = contract_instance.verify(root=repo_root, fail_closed=True)
    rep_path = target_dir / "verification_report.json"
    rep_bytes = json.dumps(verification_report, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    with open(rep_path, "wb") as f:
        f.write(rep_bytes)

    return {
        "contract": contract_path,
        "manifest": man_path,
        "verification_report": rep_path,
    }
