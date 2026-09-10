"""Authoritative ML Model Registry and Governance Layer for IRIS.

Consolidates all authoritative ML model metadata, governance statuses, artifacts,
validation methodologies, calibrations, thresholds, explainability methods,
limitations, and production availability into an enforceable, deterministic,
fail-closed registry.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

# -----------------------------------------------------------------------------
# Canonical Hashes and Frozen Constants
# -----------------------------------------------------------------------------

REGISTRY_VERSION = "1.0.0"
REGISTRY_ID = "iris_ml_model_registry_v1"
SCHEMA_CONTRACT_RELPATH = "schemas/ml_model_registry_v1.contract.json"
DEFAULT_REGISTRY_RELPATH = "artifacts/ml/model_registry_v1/registry.json"
DEFAULT_MANIFEST_RELPATH = "artifacts/ml/model_registry_v1/manifest.json"
DEFAULT_REPORT_RELPATH = "artifacts/ml/model_registry_v1/verification_report.json"

# Canonical Datasets
CANONICAL_MONTHLY_PATH = "data/processed/projects_monthly.csv"
CANONICAL_MONTHLY_SHA256 = "9512A9881E17DFDED6E182D87A8DFB1C4EDBD36C0D9B8A7DA9FD1ABB7E002FBF"

CANONICAL_COMPLETED_PATH = "data/processed/projects_completed.csv"
CANONICAL_COMPLETED_SHA256 = "89BEA84FD68A22E327090C1E4E4533F5BCD745ADCA61EB4E66172EE9023BB910"

# Locked Schedule Model Artifacts
SCHEDULE_LEGACY_ARTIFACT_PATH = "artifacts/ml/schedule_extension_3m/legacy_catboost/model.cbm"
SCHEDULE_LEGACY_ARTIFACT_SHA256 = "59586004F5967602651156E0A26FE564015F240958F5416CBB565E4755C524EE"

SCHEDULE_MODERN_ARTIFACT_PATH = "artifacts/ml/schedule_extension_3m/modern_logistic/model.joblib"
SCHEDULE_MODERN_ARTIFACT_SHA256 = "679D9768869088BA8CEE297577B1935DCF903F00B38697BF9A3FFA2F7DEB5082"

# Governance States
GOVERNANCE_LOCKED_PRODUCTION = "LOCKED_PRODUCTION"
GOVERNANCE_VIABLE_WITH_LIMITATIONS = "VIABLE_WITH_LIMITATIONS"
GOVERNANCE_NOT_READY_FOR_PRODUCTION = "NOT_READY_FOR_PRODUCTION"

VALID_GOVERNANCE_STATES = frozenset({
    GOVERNANCE_LOCKED_PRODUCTION,
    GOVERNANCE_VIABLE_WITH_LIMITATIONS,
    GOVERNANCE_NOT_READY_FOR_PRODUCTION,
})

# Production Availability States
AVAILABILITY_AVAILABLE = "AVAILABLE"
AVAILABILITY_NOT_AVAILABLE = "NOT_AVAILABLE"
AVAILABILITY_EVALUATION_ONLY = "EVALUATION_ONLY"
AVAILABILITY_INELIGIBLE = "INELIGIBLE"

VALID_AVAILABILITY_STATES = frozenset({
    AVAILABILITY_AVAILABLE,
    AVAILABILITY_NOT_AVAILABLE,
    AVAILABILITY_EVALUATION_ONLY,
    AVAILABILITY_INELIGIBLE,
})

# Domain Aliases
DOMAIN_ALIASES: dict[str, str] = {
    "schedule": "schedule_3m",
    "schedule_3m": "schedule_3m",
    "schedule_extension": "schedule_3m",
    "schedule_extension_3m": "schedule_3m",
    "cost": "cost_overrun",
    "cost_overrun": "cost_overrun",
    "cost_overrun_3m": "cost_overrun",
    "implementation": "implementation_risk",
    "implementation_risk": "implementation_risk",
    "implementation_risk_3m": "implementation_risk",
    "progress_stagnation": "implementation_risk",
}


# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------

class ModelRegistryError(Exception):
    """Base error for ML model registry operations."""


class ModelRegistryVerificationError(ModelRegistryError):
    """Raised when model registry fails verification or integrity checks."""


# -----------------------------------------------------------------------------
# Core Registry Class
# -----------------------------------------------------------------------------

class ModelRegistry:
    """Authoritative, deterministic, auditable ML model registry for IRIS."""

    def __init__(
        self,
        registry_data: dict[str, Any],
        manifest_data: dict[str, Any] | None = None,
        root: Path | None = None,
    ) -> None:
        self._root = (root or Path.cwd()).resolve()
        self._registry = copy.deepcopy(registry_data)
        self._manifest = copy.deepcopy(manifest_data) if manifest_data else None

        # Validate on initialization
        errors = self.validate_registry(self._registry)
        if errors:
            raise ModelRegistryError(
                f"Invalid registry data structure: {'; '.join(errors)}"
            )

    @classmethod
    def load(
        cls,
        registry_path: Path | str | None = None,
        root: Path | None = None,
        manifest_path: Path | str | None = None,
    ) -> ModelRegistry:
        """Load registry from authoritative JSON file."""
        repo_root = (root or Path.cwd()).resolve()
        path = (
            Path(registry_path).resolve()
            if registry_path
            else (repo_root / DEFAULT_REGISTRY_RELPATH).resolve()
        )

        if not path.is_file():
            raise FileNotFoundError(f"Model registry file not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                registry_data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ModelRegistryError(f"Corrupted registry JSON at {path}: {exc}") from exc

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

        return cls(registry_data=registry_data, manifest_data=manifest_data, root=repo_root)

    # -------------------------------------------------------------------------
    # Accessors
    # -------------------------------------------------------------------------

    def get_registry(self) -> dict[str, Any]:
        """Return raw authoritative registry data copy."""
        return copy.deepcopy(self._registry)

    def to_dict(self, mask_internal_paths: bool = False) -> dict[str, Any]:
        """Return registry dictionary, optionally masking absolute filesystem paths."""
        data = copy.deepcopy(self._registry)
        if mask_internal_paths:
            data = self._mask_paths(data)
        return data

    @property
    def version(self) -> str:
        return str(self._registry.get("registry_version", ""))

    @property
    def registry_id(self) -> str:
        return str(self._registry.get("registry_id", ""))

    def list_domains(self) -> list[str]:
        """Return sorted list of authoritative domain identifiers."""
        return sorted(list(self._registry.get("domains", {}).keys()))

    def normalize_domain_id(self, domain_name: str) -> str:
        """Resolve domain identifier or alias to canonical domain ID."""
        key = domain_name.strip().lower()
        if key in DOMAIN_ALIASES:
            return DOMAIN_ALIASES[key]
        if key in self._registry.get("domains", {}):
            return key
        raise KeyError(f"Unknown domain identifier: '{domain_name}'. Valid domains: {self.list_domains()}")

    def get_domain(self, domain_name: str) -> dict[str, Any]:
        """Retrieve authoritative domain record."""
        canonical_id = self.normalize_domain_id(domain_name)
        domain = self._registry["domains"].get(canonical_id)
        if domain is None:
            raise KeyError(f"Domain '{canonical_id}' not found in registry.")
        return copy.deepcopy(domain)

    def list_models(self, domain_name: str | None = None) -> list[str]:
        """List model IDs, optionally filtered by domain."""
        if domain_name is not None:
            domain = self.get_domain(domain_name)
            return sorted(list(domain.get("models", {}).keys()))

        model_ids: list[str] = []
        for d in self._registry.get("domains", {}).values():
            for m in d.get("models", {}).values():
                model_ids.append(m["model_id"])
        return sorted(model_ids)

    def get_model(
        self,
        model_identifier: str | None = None,
        domain: str | None = None,
        regime: str | None = None,
        candidate_type: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve a specific model record by ID or by (domain, regime/candidate_type)."""
        if model_identifier:
            target_id = model_identifier.strip().lower()
            for d in self._registry.get("domains", {}).values():
                for m_key, m_val in d.get("models", {}).items():
                    if (
                        m_key.lower() == target_id
                        or m_val.get("model_id", "").lower() == target_id
                        or m_val.get("model_name", "").lower() == target_id
                    ):
                        return copy.deepcopy(m_val)
            raise KeyError(f"Model with identifier '{model_identifier}' not found in registry.")

        if domain:
            dom = self.get_domain(domain)
            models = dom.get("models", {})

            if regime:
                target_regime = regime.strip().upper()
                for m_val in models.values():
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
            raise ValueError(f"Ambiguous query: domain '{domain}' has multiple models. Specify regime or candidate_type.")

        raise ValueError("Must provide either model_identifier or domain (with regime or candidate_type).")

    # -------------------------------------------------------------------------
    # Fail-Closed Validation Rules
    # -------------------------------------------------------------------------

    @classmethod
    def validate_registry(cls, registry_dict: dict[str, Any] | None) -> list[str]:
        """Validate structure and fail-closed governance invariants."""
        errors: list[str] = []
        if not isinstance(registry_dict, dict):
            return ["Registry data must be a JSON object"]

        # Required top-level fields
        required_top = [
            "registry_version",
            "registry_id",
            "generation_policy",
            "canonical_datasets",
            "source_contracts",
            "source_manifests",
            "domains",
        ]
        for field in required_top:
            if field not in registry_dict:
                errors.append(f"Missing required top-level field: '{field}'")

        if registry_dict.get("registry_id") != REGISTRY_ID:
            errors.append(
                f"Invalid registry_id: expected '{REGISTRY_ID}', got '{registry_dict.get('registry_id')}'"
            )

        if registry_dict.get("registry_version") != REGISTRY_VERSION:
            errors.append(
                f"Invalid registry_version: expected '{REGISTRY_VERSION}', got '{registry_dict.get('registry_version')}'"
            )

        # Domains check
        domains = registry_dict.get("domains")
        if not isinstance(domains, dict) or not domains:
            errors.append("Field 'domains' must be a non-empty object mapping.")
            return errors

        required_domain_keys = {"schedule_3m", "cost_overrun", "implementation_risk"}
        missing_domains = required_domain_keys - set(domains.keys())
        if missing_domains:
            errors.append(f"Registry missing required domains: {sorted(list(missing_domains))}")

        seen_model_ids: set[str] = set()

        for d_id, d_data in domains.items():
            if not isinstance(d_data, dict):
                errors.append(f"Domain '{d_id}' must be an object")
                continue

            gov_status = d_data.get("governance_status")
            if gov_status not in VALID_GOVERNANCE_STATES:
                errors.append(f"Domain '{d_id}' has invalid governance_status: '{gov_status}'")

            avail_status = d_data.get("production_availability")
            if avail_status not in VALID_AVAILABILITY_STATES:
                errors.append(f"Domain '{d_id}' has invalid production_availability: '{avail_status}'")

            # Domain invariant: NOT_READY_FOR_PRODUCTION cannot be AVAILABLE
            if gov_status == GOVERNANCE_NOT_READY_FOR_PRODUCTION and avail_status == AVAILABILITY_AVAILABLE:
                errors.append(
                    f"Domain '{d_id}': NOT_READY_FOR_PRODUCTION domain cannot have production_availability=AVAILABLE"
                )

            models = d_data.get("models")
            if not isinstance(models, dict) or not models:
                errors.append(f"Domain '{d_id}' must contain a non-empty 'models' object mapping.")
                continue

            for m_key, m_data in models.items():
                if not isinstance(m_data, dict):
                    errors.append(f"Model '{d_id}.{m_key}' must be an object")
                    continue

                m_id = m_data.get("model_id")
                if not m_id:
                    errors.append(f"Model '{d_id}.{m_key}' is missing 'model_id'")
                else:
                    if m_id in seen_model_ids:
                        errors.append(f"Duplicate model_id detected: '{m_id}'")
                    seen_model_ids.add(m_id)

                m_gov = m_data.get("governance_status")
                if m_gov not in VALID_GOVERNANCE_STATES:
                    errors.append(f"Model '{d_id}.{m_key}' has invalid governance_status: '{m_gov}'")

                m_avail = m_data.get("production_availability")
                if m_avail not in VALID_AVAILABILITY_STATES:
                    errors.append(f"Model '{d_id}.{m_key}' has invalid production_availability: '{m_avail}'")

                # Invariant 1: LOCKED_PRODUCTION cannot be NOT_AVAILABLE without explicit exception
                if m_gov == GOVERNANCE_LOCKED_PRODUCTION and m_avail == AVAILABILITY_NOT_AVAILABLE:
                    errors.append(
                        f"Model '{d_id}.{m_key}': LOCKED_PRODUCTION model cannot have production_availability=NOT_AVAILABLE"
                    )

                # Invariant 2: NOT_READY_FOR_PRODUCTION must never be AVAILABLE
                if m_gov == GOVERNANCE_NOT_READY_FOR_PRODUCTION and m_avail == AVAILABILITY_AVAILABLE:
                    errors.append(
                        f"Model '{d_id}.{m_key}': NOT_READY_FOR_PRODUCTION model must not be marked AVAILABLE"
                    )

                # Invariant 3: EVALUATION_ONLY must never be AVAILABLE
                if m_avail == AVAILABILITY_EVALUATION_ONLY and m_avail == AVAILABILITY_AVAILABLE:
                    errors.append(
                        f"Model '{d_id}.{m_key}': EVALUATION_ONLY model must not be marked AVAILABLE"
                    )

                # Artifact checks if AVAILABLE
                if m_avail == AVAILABILITY_AVAILABLE:
                    artifact = m_data.get("artifact")
                    if not artifact or not isinstance(artifact, dict):
                        errors.append(f"Available model '{d_id}.{m_key}' must specify a valid artifact object.")
                    else:
                        if not artifact.get("path"):
                            errors.append(f"Available model '{d_id}.{m_key}' artifact missing 'path'.")
                        if not artifact.get("sha256"):
                            errors.append(f"Available model '{d_id}.{m_key}' artifact missing 'sha256'.")

                # Scientific metadata presence
                if not m_data.get("target"):
                    errors.append(f"Model '{d_id}.{m_key}' missing required 'target'")
                if "horizon_months" not in m_data:
                    errors.append(f"Model '{d_id}.{m_key}' missing required 'horizon_months'")
                if not m_data.get("validation_methodology"):
                    errors.append(f"Model '{d_id}.{m_key}' missing required 'validation_methodology'")
                if not m_data.get("embargo_policy"):
                    errors.append(f"Model '{d_id}.{m_key}' missing required 'embargo_policy'")
                if not m_data.get("features"):
                    errors.append(f"Model '{d_id}.{m_key}' missing required 'features'")
                if not m_data.get("limitations"):
                    errors.append(f"Model '{d_id}.{m_key}' missing required 'limitations'")

        return errors

    # -------------------------------------------------------------------------
    # Verification & Hash Integrity
    # -------------------------------------------------------------------------

    def verify_hashes(self, root: Path | None = None) -> dict[str, Any]:
        """Verify SHA-256 hashes of canonical datasets and locked model artifacts."""
        repo_root = (root or self._root).resolve()
        results: dict[str, Any] = {
            "canonical_datasets": {},
            "locked_models": {},
            "all_passed": True,
        }

        # 1. Canonical datasets
        checks = [
            ("projects_monthly.csv", CANONICAL_MONTHLY_PATH, CANONICAL_MONTHLY_SHA256),
            ("projects_completed.csv", CANONICAL_COMPLETED_PATH, CANONICAL_COMPLETED_SHA256),
        ]
        for name, rel_path, expected_hash in checks:
            full_path = (repo_root / rel_path).resolve()
            if not full_path.is_file():
                results["canonical_datasets"][name] = {
                    "path": rel_path,
                    "exists": False,
                    "expected_sha256": expected_hash,
                    "actual_sha256": None,
                    "match": False,
                    "error": "File not found",
                }
                results["all_passed"] = False
            else:
                actual_hash = self._compute_sha256(full_path)
                match = (actual_hash == expected_hash)
                results["canonical_datasets"][name] = {
                    "path": rel_path,
                    "exists": True,
                    "expected_sha256": expected_hash,
                    "actual_sha256": actual_hash,
                    "match": match,
                }
                if not match:
                    results["all_passed"] = False

        # 2. Locked schedule model artifacts
        model_checks = [
            ("schedule_legacy_catboost", SCHEDULE_LEGACY_ARTIFACT_PATH, SCHEDULE_LEGACY_ARTIFACT_SHA256),
            ("schedule_modern_logistic", SCHEDULE_MODERN_ARTIFACT_PATH, SCHEDULE_MODERN_ARTIFACT_SHA256),
        ]
        for name, rel_path, expected_hash in model_checks:
            full_path = (repo_root / rel_path).resolve()
            if not full_path.is_file():
                results["locked_models"][name] = {
                    "path": rel_path,
                    "exists": False,
                    "expected_sha256": expected_hash,
                    "actual_sha256": None,
                    "match": False,
                    "error": "File not found",
                }
                results["all_passed"] = False
            else:
                actual_hash = self._compute_sha256(full_path)
                match = (actual_hash == expected_hash)
                results["locked_models"][name] = {
                    "path": rel_path,
                    "exists": True,
                    "expected_sha256": expected_hash,
                    "actual_sha256": actual_hash,
                    "match": match,
                }
                if not match:
                    results["all_passed"] = False

        return results

    def verify(self, root: Path | None = None, fail_closed: bool = True) -> dict[str, Any]:
        """Perform full validation and integrity verification."""
        repo_root = (root or self._root).resolve()

        # 1. Structural and governance validation
        val_errors = self.validate_registry(self._registry)

        # Check model artifact paths and hashes in registry
        for d_id, d_data in self._registry.get("domains", {}).items():
            for m_key, m_data in d_data.get("models", {}).items():
                if m_data.get("production_availability") == AVAILABILITY_AVAILABLE:
                    art = m_data.get("artifact")
                    if art and isinstance(art, dict) and "path" in art:
                        art_path = (repo_root / art["path"]).resolve()
                        if not art_path.is_file():
                            val_errors.append(
                                f"Model artifact not found for available model '{d_id}.{m_key}': {art['path']}"
                            )
                        elif "sha256" in art:
                            actual_art_hash = self._compute_sha256(art_path)
                            if actual_art_hash != art["sha256"]:
                                val_errors.append(
                                    f"Model artifact hash mismatch for '{d_id}.{m_key}': expected {art['sha256']}, got {actual_art_hash}"
                                )

        # 2. Hash integrity checks
        hash_results = self.verify_hashes(repo_root)

        # 3. Source references checks
        source_refs: dict[str, bool] = {}
        for c_name, c_info in self._registry.get("source_contracts", {}).items():
            c_path = (repo_root / c_info["path"]).resolve()
            source_refs[f"contract:{c_name}"] = c_path.is_file()
            if not c_path.is_file():
                val_errors.append(f"Referenced source contract not found: {c_info['path']}")

        for m_name, m_info in self._registry.get("source_manifests", {}).items():
            m_path = (repo_root / m_info["path"]).resolve()
            source_refs[f"manifest:{m_name}"] = m_path.is_file()
            if not m_path.is_file():
                val_errors.append(f"Referenced source manifest not found: {m_info['path']}")

        overall_status = "PASS" if (not val_errors and hash_results["all_passed"]) else "FAIL"

        report: dict[str, Any] = {
            "registry_version": self.version,
            "registry_id": self.registry_id,
            "overall_status": overall_status,
            "validation_errors": val_errors,
            "hash_verification": hash_results,
            "source_references_resolved": source_refs,
            "governance_summary": {
                d_id: {
                    "governance_status": d_val["governance_status"],
                    "production_availability": d_val["production_availability"],
                    "model_count": len(d_val.get("models", {})),
                }
                for d_id, d_val in self._registry.get("domains", {}).items()
            },
        }

        if fail_closed and overall_status != "PASS":
            msg = f"Model registry verification failed: {'; '.join(val_errors)}" if val_errors else "Hash verification failed"
            raise ModelRegistryVerificationError(msg)

        return report

    # -------------------------------------------------------------------------
    # Internal Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _compute_sha256(path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest().upper()

    @staticmethod
    def _mask_paths(obj: Any) -> Any:
        """Recursively sanitize absolute paths into repository-relative or masked representations."""
        if isinstance(obj, dict):
            masked: dict[str, Any] = {}
            for k, v in obj.items():
                if k == "path" and isinstance(v, str):
                    # Keep relative paths as is, mask absolute paths
                    p = Path(v)
                    if p.is_absolute():
                        masked[k] = p.name
                    else:
                        masked[k] = v.replace("\\", "/")
                else:
                    masked[k] = ModelRegistry._mask_paths(v)
            return masked
        elif isinstance(obj, list):
            return [ModelRegistry._mask_paths(item) for item in obj]
        return obj


# -----------------------------------------------------------------------------
# Registry Generation and Artifact Builder
# -----------------------------------------------------------------------------

def build_authoritative_registry_data() -> dict[str, Any]:
    """Construct the authoritative registry dictionary from existing repository contracts and artifacts."""
    return {
        "$schema": f"../{SCHEMA_CONTRACT_RELPATH}",
        "contract_name": "ml_model_registry_v1",
        "registry_version": REGISTRY_VERSION,
        "registry_id": REGISTRY_ID,
        "description": "Authoritative frozen ML Model Registry and Governance layer for IRIS.",
        "generation_policy": "deterministic_authoritative_consolidation",
        "canonical_datasets": {
            "projects_monthly.csv": {
                "path": CANONICAL_MONTHLY_PATH,
                "sha256": CANONICAL_MONTHLY_SHA256,
                "description": "Cleaned, standardized monthly panel of ongoing infrastructure projects.",
            },
            "projects_completed.csv": {
                "path": CANONICAL_COMPLETED_PATH,
                "sha256": CANONICAL_COMPLETED_SHA256,
                "description": "Historical records of completed projects used for cross-sectional study.",
            },
        },
        "source_contracts": {
            "schedule_extension_3m_v1": {
                "path": "schemas/schedule_extension_3m_v1.contract.json",
                "version": "1.0.0",
                "description": "Frozen ML data contract for 3-month schedule extension prediction.",
            },
            "cost_overrun_v1": {
                "path": "schemas/cost_overrun_v1.contract.json",
                "version": "1.0.0",
                "description": "Frozen ML data contract and target definition for cost overrun prediction.",
            },
            "implementation_risk_v1": {
                "path": "schemas/implementation_risk_v1.contract.json",
                "version": "1.0.0",
                "description": "Frozen ML data contract and target definition for physical progress stagnation.",
            },
        },
        "source_manifests": {
            "schedule_extension_3m": {
                "path": "artifacts/ml/schedule_extension_3m/manifest.json",
                "description": "Authoritative manifest of locked schedule extension models.",
            },
            "schedule_final_evaluation": {
                "path": "artifacts/ml/schedule_extension_3m/final_evaluation/manifest.json",
                "description": "Strict walk-forward evaluation manifest for schedule extension models.",
            },
            "cost_overrun_model_v1": {
                "path": "artifacts/ml/cost_overrun_model_v1/manifest.json",
                "description": "PR-07 walk-forward evaluation manifest for cost overrun models.",
            },
            "implementation_risk_model_v1": {
                "path": "artifacts/ml/implementation_risk_model_v1/manifest.json",
                "description": "PR-09 walk-forward evaluation manifest for implementation risk models.",
            },
            "unified_risk_serving_v1": {
                "path": "artifacts/ml/unified_risk_serving_v1/manifest.json",
                "description": "PR-10 multi-domain unified risk serving manifest.",
            },
            "unified_risk_intelligence_v1": {
                "path": "artifacts/ml/unified_risk_intelligence_v1/manifest.json",
                "description": "PR-12 multi-domain unified risk profile and intelligence manifest.",
            },
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
                    "Operational production domain. Rigorously validated under PR-03 and PR-05 strict "
                    "walk-forward evaluation. Legacy and modern regimes remain separate with locked model artifacts."
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
                        "eligibility_population": "Ongoing infrastructure projects observed continuously over forward 3-month window in Segments 1-3.",
                        "training_metadata": {
                            "start_month": "2023-01",
                            "cutoff_month": "2025-03",
                            "target_matures_by": "2025-06",
                            "training_row_count": 25406,
                            "positive_row_count": 2634,
                            "negative_row_count": 22772,
                            "hyperparameters": {
                                "iterations": 300,
                                "learning_rate": 0.05,
                                "depth": 5,
                                "l2_leaf_reg": 3.0,
                                "random_seed": 20260829,
                                "auto_class_weights": None,
                            },
                        },
                        "validation_methodology": "strict_walk_forward_expanding_window (12 evaluation folds, 2023-07 to 2025-03)",
                        "embargo_policy": "strict_walk_forward (T_train + 3 < E_eval)",
                        "features": {
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
                        "artifact": {
                            "path": SCHEDULE_LEGACY_ARTIFACT_PATH,
                            "sha256": SCHEDULE_LEGACY_ARTIFACT_SHA256,
                            "format": "cbm",
                            "size_bytes": 562232,
                            "version": "1.0.0",
                        },
                        "performance_metrics": {
                            "evaluation_folds": 12,
                            "evaluation_rows": 16999,
                            "positives": 1606,
                            "prevalence": 0.094476,
                            "average_precision": 0.407094,
                            "roc_auc": 0.806439,
                            "brier_score": 0.071988,
                            "precision_at_0_5": 0.542553,
                            "recall_at_0_5": 0.254047,
                            "f1_at_0_5": 0.346056,
                        },
                        "calibration": {
                            "method": "uncalibrated_raw_probabilities",
                            "status": "evaluated_uncalibrated_retained",
                            "limitations": "Platt scaling evaluated in PR-05 but raw probabilities retained for lower Brier score and operational monotonicity.",
                        },
                        "threshold_policy": {
                            "policy": "operational_decision_rule",
                            "threshold": 0.50,
                            "availability": AVAILABILITY_AVAILABLE,
                        },
                        "explainability": {
                            "method": "TreeSHAP",
                            "model_space_semantics": "log-odds / marginal tree contribution",
                            "limitations": "Explanations represent non-causal statistical associations based on reporting patterns.",
                        },
                        "governance_status": GOVERNANCE_LOCKED_PRODUCTION,
                        "production_availability": AVAILABILITY_AVAILABLE,
                        "intended_use": "Early operational screening of schedule extension risk in legacy reporting regime (pre-July 2025).",
                        "prohibited_use": "Autonomous contractual penalties, financial withholding, or project termination without human review.",
                        "limitations": [
                            "Legacy reporting quirks and unstandardized project codes in Segments 1-3.",
                            "MoSPI Flash Report administrative reporting lag.",
                            "Non-causal statistical associations.",
                        ],
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
                        "eligibility_population": "Ongoing infrastructure projects observed continuously over forward 3-month window in Segment 4 (July 2025 redesign onward).",
                        "training_metadata": {
                            "start_month": "2025-07",
                            "cutoff_month": "2026-04",
                            "target_matures_by": "2026-07",
                            "training_row_count": 11899,
                            "positive_row_count": 4327,
                            "negative_row_count": 7572,
                            "hyperparameters": {
                                "penalty": "l2",
                                "C": 1.0,
                                "solver": "lbfgs",
                                "max_iter": 2000,
                                "class_weight": None,
                                "random_state": 20260829,
                            },
                        },
                        "validation_methodology": "strict_walk_forward_expanding_window (5 evaluation folds, 2025-12 to 2026-04)",
                        "embargo_policy": "strict_walk_forward (T_train + 3 < E_eval)",
                        "features": {
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
                        "artifact": {
                            "path": SCHEDULE_MODERN_ARTIFACT_PATH,
                            "sha256": SCHEDULE_MODERN_ARTIFACT_SHA256,
                            "format": "joblib",
                            "size_bytes": 7145,
                            "version": "1.0.0",
                        },
                        "performance_metrics": {
                            "evaluation_folds": 5,
                            "evaluation_rows": 8190,
                            "positives": 3680,
                            "prevalence": 0.449328,
                            "average_precision": 0.758717,
                            "roc_auc": 0.841930,
                            "brier_score": 0.191617,
                            "precision_at_0_5": 0.808252,
                            "recall_at_0_5": 0.361957,
                            "f1_at_0_5": 0.500000,
                        },
                        "calibration": {
                            "method": "uncalibrated_raw_probabilities",
                            "status": "evaluated_uncalibrated_retained",
                            "limitations": "Platt scaling evaluated in PR-05 with conditional improvement; raw probabilities retained for operational consistency.",
                        },
                        "threshold_policy": {
                            "policy": "operational_decision_rule",
                            "threshold": 0.50,
                            "availability": AVAILABILITY_AVAILABLE,
                        },
                        "explainability": {
                            "method": "StandardizedCoefficients",
                            "model_space_semantics": "log-odds contribution",
                            "limitations": "Linear associations in normalized feature space; non-causal.",
                        },
                        "governance_status": GOVERNANCE_LOCKED_PRODUCTION,
                        "production_availability": AVAILABILITY_AVAILABLE,
                        "intended_use": "Early operational screening of schedule extension risk in modern 6-digit reporting regime (July 2025 onward).",
                        "prohibited_use": "Autonomous contractual penalties, financial withholding, or project termination without human review.",
                        "limitations": [
                            "Shorter longitudinal history in Segment 4 (July 2025 to July 2026).",
                            "MoSPI administrative reporting changes after redesign.",
                            "Non-causal statistical associations.",
                        ],
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
                        "eligibility_population": "Actively ongoing infrastructure projects with continuous forward 3-month observation and baseline cost > 0.",
                        "training_metadata": None,
                        "validation_methodology": "strict_walk_forward_expanding_window (12 LEGACY folds, 5 MODERN folds)",
                        "embargo_policy": "strict_walk_forward (T_train + 3 < E_eval)",
                        "features": {
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
                        "artifact": None,
                        "performance_metrics": {
                            "legacy_micro_ap": 0.022856,
                            "legacy_macro_ap": 0.030260,
                            "legacy_roc_auc": 0.558448,
                            "modern_micro_ap": 0.021013,
                            "modern_macro_ap": 0.022169,
                            "modern_roc_auc": 0.389548,
                        },
                        "calibration": {
                            "method": "balanced_class_weight_rescaling",
                            "status": "research_only",
                            "limitations": "Severe miscalibration due to class rebalancing; Brier score > 0.17 vs 0.017 prevalence baseline.",
                        },
                        "threshold_policy": {
                            "policy": "research_only",
                            "threshold": None,
                            "availability": AVAILABILITY_NOT_AVAILABLE,
                        },
                        "explainability": {
                            "method": "LogisticCoefficients",
                            "model_space_semantics": "log-odds contribution",
                            "limitations": "Research-only baseline; low discriminatory power.",
                        },
                        "governance_status": GOVERNANCE_NOT_READY_FOR_PRODUCTION,
                        "production_availability": AVAILABILITY_EVALUATION_ONLY,
                        "intended_use": "Research baseline comparison for cost overrun modeling feasibility.",
                        "prohibited_use": "Operational scoring, production decision gating, or capital allocation.",
                        "limitations": [
                            "Severe class imbalance (~2.18% positive rate).",
                            "Near-zero predictive lift over prevalence baseline.",
                            "Administrative approvals occur externally to project telemetry.",
                        ],
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
                        "eligibility_population": "Actively ongoing infrastructure projects with continuous forward 3-month observation and baseline cost > 0.",
                        "training_metadata": None,
                        "validation_methodology": "strict_walk_forward_expanding_window (12 LEGACY folds, 5 MODERN folds)",
                        "embargo_policy": "strict_walk_forward (T_train + 3 < E_eval)",
                        "features": {
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
                        "artifact": None,
                        "performance_metrics": {
                            "legacy_micro_ap": 0.027919,
                            "legacy_macro_ap": 0.047040,
                            "legacy_roc_auc": 0.602087,
                            "legacy_brier_score": 0.018344,
                            "modern_micro_ap": 0.018076,
                            "modern_macro_ap": 0.038165,
                            "modern_roc_auc": 0.528690,
                            "modern_brier_score": 0.019064,
                        },
                        "calibration": {
                            "method": "uncalibrated_raw_probabilities",
                            "status": "research_only",
                            "limitations": "Low absolute probabilities; highest Brier reliability but insufficient precision.",
                        },
                        "threshold_policy": {
                            "policy": "research_only",
                            "threshold": None,
                            "availability": AVAILABILITY_NOT_AVAILABLE,
                        },
                        "explainability": {
                            "method": "TreeSHAP",
                            "model_space_semantics": "log-odds contribution",
                            "limitations": "Research-only candidate; feature importance heavily dominated by project age and expenditure ratio.",
                        },
                        "governance_status": GOVERNANCE_NOT_READY_FOR_PRODUCTION,
                        "production_availability": AVAILABILITY_EVALUATION_ONLY,
                        "intended_use": "Research exploration of non-linear cost escalation patterns.",
                        "prohibited_use": "Operational scoring, production decision gating, or capital allocation.",
                        "limitations": [
                            "Severe class imbalance (~2.18% positive rate).",
                            "Micro average precision < 0.03 in both regimes.",
                            "External political and fiscal approval dynamics.",
                        ],
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
                        "eligibility_population": "Actively ongoing infrastructure projects with reported physical progress in [0, 100) and continuous 3-month forward observation.",
                        "training_metadata": None,
                        "validation_methodology": "strict_walk_forward_expanding_window (6 LEGACY folds, 5 MODERN folds)",
                        "embargo_policy": "strict_walk_forward (T_train + 3 < E_eval)",
                        "features": {
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
                        "artifact": None,
                        "performance_metrics": {
                            "legacy_micro_ap": 0.562873,
                            "legacy_macro_ap": 0.556955,
                            "legacy_roc_auc": 0.786989,
                            "legacy_brier_score": 0.166372,
                            "modern_micro_ap": 0.222885,
                            "modern_macro_ap": 0.283897,
                            "modern_roc_auc": 0.516375,
                            "modern_brier_score": 0.194695,
                        },
                        "calibration": {
                            "method": "uncalibrated_raw_probabilities",
                            "status": "research_only",
                            "limitations": "Under-predicts stagnation in Modern regime.",
                        },
                        "threshold_policy": {
                            "policy": "research_only",
                            "threshold": None,
                            "availability": AVAILABILITY_NOT_AVAILABLE,
                        },
                        "explainability": {
                            "method": "LogisticCoefficients",
                            "model_space_semantics": "log-odds contribution",
                            "limitations": "Linear baseline; lower discriminatory power than gradient boosted challenger.",
                        },
                        "governance_status": GOVERNANCE_VIABLE_WITH_LIMITATIONS,
                        "production_availability": AVAILABILITY_EVALUATION_ONLY,
                        "intended_use": "Linear baseline benchmark for physical progress stagnation.",
                        "prohibited_use": "Autonomous operational gating without human engineering review.",
                        "limitations": [
                            "Regime divergence between Legacy and Modern reporting dynamics.",
                            "Underperforms non-linear tree models by ~0.12 PR-AUC in Legacy.",
                            "Administrative reporting batching in physical progress telemetry.",
                        ],
                    },
                    "challenger": {
                        "model_id": "implementation_risk_challenger_catboost",
                        "model_name": "catboost_unweighted",
                        "model_version": "1.0.0",
                        "model_family": "CatBoostClassifier",
                        "domain": "implementation_risk",
                        "regime": "CROSS_REGIME",
                        "candidate_type": "challenger",
                        "recommendation_status": "RECOMMENDED_CHALLENGER",
                        "target": "target_progress_stagnation_3m",
                        "target_definition": "Y(i,T) = 1 if physical_progress(T+3) - physical_progress(T) <= 1e-6, else 0; 0 <= physical_progress(T) < 100.",
                        "horizon_months": 3,
                        "eligibility_population": "Actively ongoing infrastructure projects with reported physical progress in [0, 100) and continuous 3-month forward observation.",
                        "training_metadata": None,
                        "validation_methodology": "strict_walk_forward_expanding_window (6 LEGACY folds, 5 MODERN folds)",
                        "embargo_policy": "strict_walk_forward (T_train + 3 < E_eval)",
                        "features": {
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
                        "artifact": None,
                        "performance_metrics": {
                            "legacy_micro_ap": 0.687176,
                            "legacy_macro_ap": 0.689828,
                            "legacy_roc_auc": 0.866352,
                            "legacy_brier_score": 0.129145,
                            "modern_micro_ap": 0.300709,
                            "modern_macro_ap": 0.390284,
                            "modern_roc_auc": 0.645406,
                            "modern_brier_score": 0.211446,
                        },
                        "calibration": {
                            "method": "uncalibrated_raw_probabilities",
                            "status": "research_only",
                            "limitations": "Raw probabilities yield lowest Brier score; Platt scaling does not reliably improve cross-regime calibration.",
                        },
                        "threshold_policy": {
                            "policy": "research_only",
                            "threshold": None,
                            "availability": AVAILABILITY_NOT_AVAILABLE,
                        },
                        "explainability": {
                            "method": "TreeSHAP",
                            "model_space_semantics": "log-odds contribution",
                            "limitations": "Explains stagnation probability contributions from past progress deltas and project maturity.",
                        },
                        "governance_status": GOVERNANCE_VIABLE_WITH_LIMITATIONS,
                        "production_availability": AVAILABILITY_EVALUATION_ONLY,
                        "intended_use": "Evidence-based recommended challenger for decision support and early risk screening.",
                        "prohibited_use": "Autonomous operational gating without human engineering review.",
                        "limitations": [
                            "Regime divergence: performance in MODERN (PR-AUC 0.30) is lower than in LEGACY (PR-AUC 0.69).",
                            "Physical progress remains an administrative self-reported metric subject to occasional batching.",
                            "Segments 1 and 2 structurally omit physical progress.",
                            "No serialized production model artifact deployed in repository.",
                        ],
                    },
                },
            },
        },
    }


def build_registry_artifacts(
    output_dir: Path | None = None,
    root: Path | None = None,
) -> dict[str, Path]:
    """Deterministically serialize registry.json, manifest.json, and verification_report.json."""
    repo_root = (root or Path.cwd()).resolve()
    target_dir = (output_dir or repo_root / "artifacts/ml/model_registry_v1").resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Build registry data
    registry_data = build_authoritative_registry_data()
    reg_path = target_dir / "registry.json"
    reg_bytes = json.dumps(registry_data, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    with open(reg_path, "wb") as f:
        f.write(reg_bytes)
    registry_sha256 = hashlib.sha256(reg_bytes).hexdigest().upper()

    # 2. Manifest data
    manifest_data = {
        "manifest_version": "1.0.0",
        "registry_version": REGISTRY_VERSION,
        "registry_id": REGISTRY_ID,
        "contract_reference": SCHEMA_CONTRACT_RELPATH,
        "registry_sha256": registry_sha256,
        "canonical_inputs": {
            "projects_monthly.csv": CANONICAL_MONTHLY_SHA256,
            "projects_completed.csv": CANONICAL_COMPLETED_SHA256,
        },
        "locked_schedule_artifacts": {
            "legacy_catboost": SCHEDULE_LEGACY_ARTIFACT_SHA256,
            "modern_logistic": SCHEDULE_MODERN_ARTIFACT_SHA256,
        },
        "source_contracts": {
            k: v["path"] for k, v in registry_data["source_contracts"].items()
        },
        "source_manifests": {
            k: v["path"] for k, v in registry_data["source_manifests"].items()
        },
        "verification_policy": "fail_closed_strict_hash_verification",
    }
    man_path = target_dir / "manifest.json"
    man_bytes = json.dumps(manifest_data, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    with open(man_path, "wb") as f:
        f.write(man_bytes)

    # 3. Instantiate and run verify to generate deterministic verification report
    registry_instance = ModelRegistry(
        registry_data=registry_data,
        manifest_data=manifest_data,
        root=repo_root,
    )
    verification_report = registry_instance.verify(root=repo_root, fail_closed=True)
    rep_path = target_dir / "verification_report.json"
    rep_bytes = json.dumps(verification_report, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    with open(rep_path, "wb") as f:
        f.write(rep_bytes)

    return {
        "registry": reg_path,
        "manifest": man_path,
        "verification_report": rep_path,
    }
