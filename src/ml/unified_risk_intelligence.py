"""Unified Risk Intelligence and Project Risk Profile for the IRIS repository (PR-12).

This module provides a deterministic, governance-aware, and auditable project-level
risk intelligence layer (UnifiedRiskIntelligence) built on top of the PR-10
UnifiedRiskPredictor.

Key principles & guarantees:
1. Prohibition on Arbitrary Probability Aggregation:
   No single mathematically combined overall risk probability is computed (e.g.
   weighted sums, arithmetic/geometric means, or maximums). The domains have
   fundamentally disparate semantics, sample populations, and governance statuses.
2. Governance Preservation:
   - Schedule Extension: LOCKED_PRODUCTION (threshold 0.50).
   - Cost Overrun: NOT_READY_FOR_PRODUCTION (scores remain null; unavailable for production).
   - Implementation Risk: VIABLE_WITH_LIMITATIONS (human-in-the-loop decision support only;
     fails closed where unsegmented or where serialized artifact is absent).
3. Deterministic Project Risk Profile:
   Synthesizes domain-level responses into:
   - overall_status: FULL, PARTIAL, LIMITED, UNAVAILABLE, INELIGIBLE
   - coverage_status: COMPLETE_COVERAGE, PARTIAL_COVERAGE, LIMITED_COVERAGE, NO_PREDICTIVE_COVERAGE
   - priority_domains: Ordered domain list with deterministic priority levels
     (HIGH_PRIORITY, MEDIUM_PRIORITY, UNAVAILABLE, LOW_PRIORITY, INELIGIBLE).
     Unavailable domains are NEVER ranked as low risk.
   - attention_level: HIGH_ATTENTION, MEDIUM_ATTENTION, LIMITED_ASSESSMENT, ROUTINE, NO_ASSESSMENT
   - recommendations: Structured, actionable human-review recommendations.
   - limitations & governance_notes: Explicit documentation of boundaries.
   - summary: Non-causal, machine-readable intelligence synthesis.
4. Fail-Closed Validation:
   Full preservation of PR-10 validation (prohibited leakage, NaN, infinity,
   unknown features, contradictory regimes, structural gaps).
5. Immutability & Determinism:
   No state or model mutation; repeated calls and batch processing are strictly deterministic.
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from src.ml.unified_risk_predictor import (
    GOVERNANCE_STATUS_COST,
    GOVERNANCE_STATUS_IMPLEMENTATION,
    GOVERNANCE_STATUS_SCHEDULE,
    PROHIBITED_LEAKAGE_FIELDS,
    SCHEDULE_DECISION_THRESHOLD,
    SERVING_CONTRACT_VERSION,
    DomainRiskResult,
    UnifiedRiskPredictionResult,
    UnifiedRiskPredictor,
)

PROFILE_VERSION = "1.0.0"
POLICY_VERSION = "1.0.0"

# Deterministic priority thresholds for domains with valid operational probabilities
HIGH_PRIORITY_THRESHOLD = 0.50
MEDIUM_PRIORITY_THRESHOLD = 0.30

# Domain constants
SCHEDULE_DOMAIN = "schedule_extension"
COST_DOMAIN = "cost_overrun"
IMPLEMENTATION_DOMAIN = "implementation_risk"
ALL_DOMAINS = (SCHEDULE_DOMAIN, COST_DOMAIN, IMPLEMENTATION_DOMAIN)

# Profile Statuses
STATUS_FULL = "FULL"
STATUS_PARTIAL = "PARTIAL"
STATUS_LIMITED = "LIMITED"
STATUS_UNAVAILABLE = "UNAVAILABLE"
STATUS_INELIGIBLE = "INELIGIBLE"

# Coverage Statuses
COVERAGE_COMPLETE = "COMPLETE_COVERAGE"
COVERAGE_PARTIAL = "PARTIAL_COVERAGE"
COVERAGE_LIMITED = "LIMITED_COVERAGE"
COVERAGE_NONE = "NO_PREDICTIVE_COVERAGE"

# Priority Levels
PRIORITY_HIGH = "HIGH_PRIORITY"
PRIORITY_MEDIUM = "MEDIUM_PRIORITY"
PRIORITY_LOW = "LOW_PRIORITY"
PRIORITY_UNAVAILABLE = "UNAVAILABLE"
PRIORITY_INELIGIBLE = "INELIGIBLE"

# Priority sort order: High, Medium, Unavailable (must be addressed/not ignored), Low, Ineligible
PRIORITY_RANK_ORDER = {
    PRIORITY_HIGH: 1,
    PRIORITY_MEDIUM: 2,
    PRIORITY_UNAVAILABLE: 3,
    PRIORITY_LOW: 4,
    PRIORITY_INELIGIBLE: 5,
}

# Attention Levels
ATTENTION_HIGH = "HIGH_ATTENTION"
ATTENTION_MEDIUM = "MEDIUM_ATTENTION"
ATTENTION_LIMITED = "LIMITED_ASSESSMENT"
ATTENTION_ROUTINE = "ROUTINE"
ATTENTION_NONE = "NO_ASSESSMENT"

# Recommendation Codes
REC_REVIEW_SCHEDULE = "REVIEW_SCHEDULE_RISK"
REC_REVIEW_IMPLEMENTATION = "REVIEW_IMPLEMENTATION_PROGRESS"
REC_COST_NOT_READY = "COST_RISK_NOT_PRODUCTION_READY"
REC_INSUFFICIENT_COVERAGE = "INSUFFICIENT_DOMAIN_COVERAGE"
REC_IMPLEMENTATION_LIMITATIONS = "IMPLEMENTATION_MODEL_LIMITATIONS"
REC_STRUCTURAL_LIMITATION = "STRUCTURAL_ELIGIBILITY_LIMITATION"


@dataclass(frozen=True)
class DomainPriorityItem:
    """Deterministic domain priority entry within the project profile."""

    domain: str
    status: str
    governance_status: str
    priority_level: str
    risk_score: float | None
    rank: int
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "status": self.status,
            "governance_status": self.governance_status,
            "priority_level": self.priority_level,
            "risk_score": self.risk_score,
            "rank": self.rank,
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class RecommendationItem:
    """Actionable human-review recommendation item."""

    code: str
    domain: str
    description: str
    action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "domain": self.domain,
            "description": self.description,
            "action": self.action,
        }


class UnifiedRiskIntelligence:
    """Stateless, deterministic unified risk intelligence layer for project risk profiling."""

    def __init__(
        self,
        predictor: UnifiedRiskPredictor,
        profile_version: str = PROFILE_VERSION,
        policy_version: str = POLICY_VERSION,
    ) -> None:
        self.predictor = predictor
        self.profile_version = profile_version
        self.policy_version = policy_version

    @classmethod
    def load(
        cls,
        artifacts_dir: Path | str | None = None,
        verify_hashes: bool = True,
    ) -> "UnifiedRiskIntelligence":
        """Load underlying serving predictor and initialize the intelligence layer."""
        predictor = UnifiedRiskPredictor.load(
            artifacts_dir=artifacts_dir,
            verify_hashes=verify_hashes,
        )
        return cls(predictor=predictor)

    def _normalize_domain_dict(self, domain_data: Any) -> dict[str, Any]:
        """Convert DomainRiskResult or dict to uniform dictionary."""
        if hasattr(domain_data, "to_dict"):
            return domain_data.to_dict()
        if isinstance(domain_data, dict):
            return dict(domain_data)
        raise ValueError(f"Unsupported domain data type: {type(domain_data)}")

    def _classify_profile_status(
        self,
        available_count: int,
        unavailable_count: int,
        ineligible_count: int,
        total_domains: int = 3,
    ) -> str:
        """Deterministically classify overall profile status.

        Rules:
        - FULL: All applicable domains are AVAILABLE (available_count == total).
        - PARTIAL: At least one domain is AVAILABLE, one or more are NOT_AVAILABLE,
                   and zero domains are INELIGIBLE.
        - LIMITED: At least one domain is AVAILABLE or decision-support, but one or more
                   domains are INELIGIBLE (structural source omissions).
        - UNAVAILABLE: Zero domains are AVAILABLE, but at least one domain is NOT_AVAILABLE.
        - INELIGIBLE: All applicable domains are structurally INELIGIBLE (ineligible_count == total).
        """
        if available_count == total_domains:
            return STATUS_FULL
        if ineligible_count == total_domains:
            return STATUS_INELIGIBLE
        if available_count == 0 and unavailable_count > 0:
            return STATUS_UNAVAILABLE
        if available_count > 0 and ineligible_count > 0:
            return STATUS_LIMITED
        if available_count > 0 and unavailable_count > 0:
            return STATUS_PARTIAL
        return STATUS_UNAVAILABLE

    def _classify_coverage(
        self,
        available_count: int,
        unavailable_count: int,
        ineligible_count: int,
        total_domains: int = 3,
    ) -> str:
        """Deterministically classify coverage status.

        Rules:
        - COMPLETE_COVERAGE: All domains available (available == total).
        - PARTIAL_COVERAGE: At least one domain available, some unavailable, none ineligible.
        - LIMITED_COVERAGE: At least one domain available, but at least one ineligible.
        - NO_PREDICTIVE_COVERAGE: Zero domains available.
        """
        if available_count == total_domains:
            return COVERAGE_COMPLETE
        if available_count == 0:
            return COVERAGE_NONE
        if ineligible_count > 0:
            return COVERAGE_LIMITED
        return COVERAGE_PARTIAL

    def _evaluate_domain_priority(
        self,
        domain_name: str,
        domain_dict: dict[str, Any],
    ) -> tuple[str, str]:
        """Evaluate deterministic priority level and rationale for a single domain.

        Rules:
        - Only AVAILABLE domains with valid probabilities receive probability-based priority.
        - Unavailable domains receive 'UNAVAILABLE' (never classified as low risk).
        - Ineligible domains receive 'INELIGIBLE'.
        """
        status = domain_dict.get("status", "NOT_AVAILABLE")
        score = domain_dict.get("risk_score")
        gov = domain_dict.get("operational_status", "UNKNOWN")

        if status == "INELIGIBLE":
            return (
                PRIORITY_INELIGIBLE,
                f"Domain '{domain_name}' is structurally ineligible for this observation segment.",
            )

        if status != "AVAILABLE" or score is None:
            if domain_name == COST_DOMAIN:
                rationale = (
                    "Cost overrun prediction is unassessed due to NOT_READY_FOR_PRODUCTION "
                    "governance; missing score must not be interpreted as low risk."
                )
            elif domain_name == IMPLEMENTATION_DOMAIN:
                rationale = (
                    "Implementation risk prediction is unassessed due to absence of serialized "
                    "production inference artifact; missing score must not be interpreted as low risk."
                )
            else:
                rationale = (
                    f"Domain '{domain_name}' risk prediction is unassessed; missing score "
                    "must not be interpreted as low risk."
                )
            return PRIORITY_UNAVAILABLE, rationale

        # Status is AVAILABLE with valid score
        if score >= HIGH_PRIORITY_THRESHOLD:
            level = PRIORITY_HIGH
            rationale = (
                f"Domain '{domain_name}' risk score ({score:.4f}) meets or exceeds operational "
                f"threshold ({HIGH_PRIORITY_THRESHOLD:.2f}), indicating elevated risk under {gov}."
            )
        elif score >= MEDIUM_PRIORITY_THRESHOLD:
            level = PRIORITY_MEDIUM
            rationale = (
                f"Domain '{domain_name}' risk score ({score:.4f}) indicates moderate/borderline "
                f"risk under {gov} (threshold {HIGH_PRIORITY_THRESHOLD:.2f})."
            )
        else:
            level = PRIORITY_LOW
            rationale = (
                f"Domain '{domain_name}' risk score ({score:.4f}) is below moderate cutoff "
                f"({MEDIUM_PRIORITY_THRESHOLD:.2f}) under {gov}."
            )

        return level, rationale

    def _build_priority_ordering(
        self,
        domains: dict[str, dict[str, Any]],
    ) -> list[DomainPriorityItem]:
        """Build deterministically ranked domain priority list.

        Ranking order:
        1. Priority level rank: HIGH_PRIORITY (1) > MEDIUM_PRIORITY (2) > UNAVAILABLE (3) > LOW_PRIORITY (4) > INELIGIBLE (5)
        2. Within same priority level, score descending (None sorted last)
        3. Tie-breaker: domain name alphabetical
        """
        items: list[tuple[int, float, str, DomainPriorityItem]] = []

        for domain_name in ALL_DOMAINS:
            d_dict = domains.get(domain_name, {})
            status = d_dict.get("status", "NOT_AVAILABLE")
            gov = d_dict.get("operational_status", "UNKNOWN")
            score = d_dict.get("risk_score")

            priority_level, rationale = self._evaluate_domain_priority(domain_name, d_dict)
            level_rank = PRIORITY_RANK_ORDER.get(priority_level, 99)

            score_sort_val = -score if (score is not None and not math.isnan(score)) else 999.0

            item = DomainPriorityItem(
                domain=domain_name,
                status=status,
                governance_status=gov,
                priority_level=priority_level,
                risk_score=score,
                rank=0,  # assigned after sort
                rationale=rationale,
            )
            items.append((level_rank, score_sort_val, domain_name, item))

        # Deterministic sort
        items.sort(key=lambda x: (x[0], x[1], x[2]))

        ranked_items: list[DomainPriorityItem] = []
        for idx, (_, _, _, base_item) in enumerate(items, start=1):
            ranked_items.append(
                DomainPriorityItem(
                    domain=base_item.domain,
                    status=base_item.status,
                    governance_status=base_item.governance_status,
                    priority_level=base_item.priority_level,
                    risk_score=base_item.risk_score,
                    rank=idx,
                    rationale=base_item.rationale,
                )
            )

        return ranked_items

    def _classify_attention_level(
        self,
        available_count: int,
        coverage_status: str,
        priority_domains: Sequence[DomainPriorityItem],
    ) -> str:
        """Deterministically derive project-level attention level.

        Rules:
        - NO_ASSESSMENT: available_count == 0 (no predictive assessment available).
        - HIGH_ATTENTION: At least one AVAILABLE domain is HIGH_PRIORITY.
        - MEDIUM_ATTENTION: At least one AVAILABLE domain is MEDIUM_PRIORITY (and none HIGH).
        - When all available domains are LOW_PRIORITY:
          - ROUTINE: Only if coverage is COMPLETE_COVERAGE (all domains assessed as low risk).
          - LIMITED_ASSESSMENT: If coverage is PARTIAL_COVERAGE or LIMITED_COVERAGE, because
            missing/unassessed domains cannot be assumed safe.
        """
        if available_count == 0:
            return ATTENTION_NONE

        available_priorities = [
            p.priority_level for p in priority_domains if p.status == "AVAILABLE"
        ]

        if PRIORITY_HIGH in available_priorities:
            return ATTENTION_HIGH

        if PRIORITY_MEDIUM in available_priorities:
            return ATTENTION_MEDIUM

        # All available domains are LOW_PRIORITY
        if coverage_status == COVERAGE_COMPLETE:
            return ATTENTION_ROUTINE

        return ATTENTION_LIMITED

    def _generate_recommendations(
        self,
        domains: dict[str, dict[str, Any]],
        coverage_status: str,
        priority_domains: Sequence[DomainPriorityItem],
    ) -> list[RecommendationItem]:
        """Generate deterministic, actionable human-review recommendations."""
        recommendations: list[RecommendationItem] = []

        # 1. Schedule review
        sched = domains.get(SCHEDULE_DOMAIN, {})
        sched_priority = next(
            (p for p in priority_domains if p.domain == SCHEDULE_DOMAIN), None
        )
        if sched_priority and sched_priority.priority_level in (
            PRIORITY_HIGH,
            PRIORITY_MEDIUM,
        ):
            score_str = f"{sched.get('risk_score', 0.0):.4f}"
            recommendations.append(
                RecommendationItem(
                    code=REC_REVIEW_SCHEDULE,
                    domain=SCHEDULE_DOMAIN,
                    description=(
                        f"Schedule extension risk is elevated ({score_str}) under the "
                        "locked production model."
                    ),
                    action="Conduct milestone and schedule contingency review with project director.",
                )
            )

        # 2. Cost overrun governance notice
        cost = domains.get(COST_DOMAIN, {})
        if cost.get("operational_status") == GOVERNANCE_STATUS_COST:
            recommendations.append(
                RecommendationItem(
                    code=REC_COST_NOT_READY,
                    domain=COST_DOMAIN,
                    description=(
                        "Cost overrun prediction is unassessed; domain is governed as "
                        "NOT_READY_FOR_PRODUCTION due to class imbalance (~2.18%)."
                    ),
                    action="Do not treat missing cost risk as safe; apply manual expenditure audits.",
                )
            )

        # 3. Coverage limitation notice
        if coverage_status in (COVERAGE_PARTIAL, COVERAGE_LIMITED, COVERAGE_NONE):
            recommendations.append(
                RecommendationItem(
                    code=REC_INSUFFICIENT_COVERAGE,
                    domain="overall",
                    description=(
                        f"Project risk assessment operates under {coverage_status}; "
                        "risk intelligence is incomplete across all three dimensions."
                    ),
                    action="Incorporate manual monitoring for unassessed and ineligible risk domains.",
                )
            )

        # 4. Implementation risk notice
        impl = domains.get(IMPLEMENTATION_DOMAIN, {})
        if impl.get("status") == "INELIGIBLE":
            recommendations.append(
                RecommendationItem(
                    code=REC_STRUCTURAL_LIMITATION,
                    domain=IMPLEMENTATION_DOMAIN,
                    description=(
                        "Implementation risk is structurally ineligible for this observation "
                        "because physical progress was not recorded in source reports."
                    ),
                    action="Refer to raw project records for non-standardized progress metrics.",
                )
            )
        elif impl.get("status") == "NOT_AVAILABLE":
            recommendations.append(
                RecommendationItem(
                    code=REC_IMPLEMENTATION_LIMITATIONS,
                    domain=IMPLEMENTATION_DOMAIN,
                    description=(
                        "Implementation risk model is governed as VIABLE_WITH_LIMITATIONS for "
                        "decision support, but lacks a deployed serialized inference artifact."
                    ),
                    action="Track contractor milestone logs and physical expenditure ratios manually.",
                )
            )

        return recommendations

    def _compile_limitations(
        self,
        domains: dict[str, dict[str, Any]],
        coverage_status: str,
    ) -> list[str]:
        """Compile explicit list of methodological and governance limitations."""
        limitations = [
            "Prohibition on Cross-Domain Aggregation: No combined overall risk probability "
            "is mathematically computed, averaged, or implied.",
            "Schedule Extension: Predictions reflect correlational statistical associations "
            "from locked models, not verified causal mechanisms.",
            "Cost Overrun: Governed as NOT_READY_FOR_PRODUCTION under PR-07; autonomous "
            "production prediction is strictly prohibited.",
            "Implementation Risk: Governed as VIABLE_WITH_LIMITATIONS under PR-09 for human-in-the-loop "
            "decision support; no serialized production inference artifact is currently deployed.",
        ]

        impl = domains.get(IMPLEMENTATION_DOMAIN, {})
        if impl.get("status") == "INELIGIBLE":
            limitations.append(
                "Structural Ineligibility: This continuous segment structurally omits physical "
                "progress columns in historical reports."
            )

        if coverage_status != COVERAGE_COMPLETE:
            limitations.append(
                "Incomplete Predictive Coverage: Missing domain risk scores represent absent "
                "or unassessed models, NEVER evidence of zero or low risk."
            )

        return limitations

    def _compile_governance_notes(
        self,
        domains: dict[str, dict[str, Any]],
        overall_status: str,
    ) -> list[str]:
        """Compile governance audit notes."""
        return [
            f"Schedule Extension Domain: Status={domains.get(SCHEDULE_DOMAIN, {}).get('status')}, "
            f"Governance={GOVERNANCE_STATUS_SCHEDULE}, DecisionThreshold={SCHEDULE_DECISION_THRESHOLD}.",
            f"Cost Overrun Domain: Status={domains.get(COST_DOMAIN, {}).get('status')}, "
            f"Governance={GOVERNANCE_STATUS_COST} (Autonomous scoring prohibited).",
            f"Implementation Risk Domain: Status={domains.get(IMPLEMENTATION_DOMAIN, {}).get('status')}, "
            f"Governance={GOVERNANCE_STATUS_IMPLEMENTATION} (Decision support only).",
            f"Profile Classification: overall_status={overall_status}, profile_version={self.profile_version}, "
            f"policy_version={self.policy_version}.",
        ]

    def _generate_intelligence_summary(
        self,
        domains: dict[str, dict[str, Any]],
        overall_status: str,
        coverage_status: str,
        attention_level: str,
        priority_domains: Sequence[DomainPriorityItem],
    ) -> str:
        """Generate concise, deterministic, non-causal machine-readable intelligence summary."""
        parts: list[str] = []

        sched = domains.get(SCHEDULE_DOMAIN, {})
        sched_status = sched.get("status")
        sched_score = sched.get("risk_score")

        if sched_status == "AVAILABLE" and sched_score is not None:
            if sched_score >= HIGH_PRIORITY_THRESHOLD:
                parts.append(
                    f"Schedule extension risk is available and elevated ({sched_score:.4f}) "
                    f"under the locked production model (threshold {HIGH_PRIORITY_THRESHOLD:.2f})."
                )
            elif sched_score >= MEDIUM_PRIORITY_THRESHOLD:
                parts.append(
                    f"Schedule extension risk is available and moderate ({sched_score:.4f}) "
                    f"under the locked production model."
                )
            else:
                parts.append(
                    f"Schedule extension risk is available and below the decision threshold "
                    f"({sched_score:.4f} < {HIGH_PRIORITY_THRESHOLD:.2f})."
                )
        elif sched_status == "INELIGIBLE":
            parts.append("Schedule extension risk is structurally ineligible for this observation.")
        else:
            parts.append("Schedule extension risk is not available.")

        cost = domains.get(COST_DOMAIN, {})
        if cost.get("operational_status") == GOVERNANCE_STATUS_COST:
            parts.append(
                "Cost overrun prediction is not available because the domain remains "
                "NOT_READY_FOR_PRODUCTION under PR-07 governance."
            )

        impl = domains.get(IMPLEMENTATION_DOMAIN, {})
        impl_status = impl.get("status")
        if impl_status == "INELIGIBLE":
            parts.append(
                "Implementation risk is ineligible due to structural absence of physical progress "
                "in this segment."
            )
        elif impl_status == "NOT_AVAILABLE":
            parts.append(
                "Implementation risk assessment is limited by the absence of a serialized "
                "production inference artifact."
            )

        parts.append(
            f"Project attention level is classified as {attention_level} under {coverage_status} "
            f"(overall profile status: {overall_status})."
        )

        return " ".join(parts)

    def evaluate_profile_from_serving(
        self, serving_result: dict[str, Any]
    ) -> dict[str, Any]:
        """Synthesize a deterministic Project Risk Profile from a PR-10 serving result."""
        project_id = serving_result.get("project_id")
        report_month = serving_result.get("report_month", "")

        domains: dict[str, dict[str, Any]] = {
            SCHEDULE_DOMAIN: self._normalize_domain_dict(
                serving_result.get(SCHEDULE_DOMAIN, {})
            ),
            COST_DOMAIN: self._normalize_domain_dict(serving_result.get(COST_DOMAIN, {})),
            IMPLEMENTATION_DOMAIN: self._normalize_domain_dict(
                serving_result.get(IMPLEMENTATION_DOMAIN, {})
            ),
        }

        # Counts
        available_count = sum(1 for d in domains.values() if d.get("status") == "AVAILABLE")
        unavailable_count = sum(
            1 for d in domains.values() if d.get("status") == "NOT_AVAILABLE"
        )
        ineligible_count = sum(
            1 for d in domains.values() if d.get("status") == "INELIGIBLE"
        )
        total_domains = len(domains)

        # Statuses
        overall_status = self._classify_profile_status(
            available_count=available_count,
            unavailable_count=unavailable_count,
            ineligible_count=ineligible_count,
            total_domains=total_domains,
        )

        coverage_status = self._classify_coverage(
            available_count=available_count,
            unavailable_count=unavailable_count,
            ineligible_count=ineligible_count,
            total_domains=total_domains,
        )

        priority_domains = self._build_priority_ordering(domains)

        attention_level = self._classify_attention_level(
            available_count=available_count,
            coverage_status=coverage_status,
            priority_domains=priority_domains,
        )

        recommendations = self._generate_recommendations(
            domains=domains,
            coverage_status=coverage_status,
            priority_domains=priority_domains,
        )

        limitations = self._compile_limitations(domains, coverage_status)
        governance_notes = self._compile_governance_notes(domains, overall_status)

        summary = self._generate_intelligence_summary(
            domains=domains,
            overall_status=overall_status,
            coverage_status=coverage_status,
            attention_level=attention_level,
            priority_domains=priority_domains,
        )

        serving_meta = serving_result.get("metadata", {})
        metadata = {
            "profile_version": self.profile_version,
            "policy_version": self.policy_version,
            "generated_deterministically": True,
            "serving_contract_version": serving_meta.get(
                "serving_contract_version", SERVING_CONTRACT_VERSION
            ),
            "continuous_segment": serving_meta.get("continuous_segment"),
            "governance": {
                SCHEDULE_DOMAIN: GOVERNANCE_STATUS_SCHEDULE,
                COST_DOMAIN: GOVERNANCE_STATUS_COST,
                IMPLEMENTATION_DOMAIN: GOVERNANCE_STATUS_IMPLEMENTATION,
            },
        }

        return {
            "project": {
                "project_identifier": project_id,
                "report_month": report_month,
            },
            "domains": domains,
            "profile": {
                "overall_status": overall_status,
                "coverage_status": coverage_status,
                "available_domain_count": available_count,
                "unavailable_domain_count": unavailable_count,
                "ineligible_domain_count": ineligible_count,
                "priority_domains": [p.to_dict() for p in priority_domains],
                "attention_level": attention_level,
                "recommendations": [r.to_dict() for r in recommendations],
                "limitations": limitations,
                "governance_notes": governance_notes,
                "summary": summary,
            },
            "metadata": metadata,
        }

    def predict_one(self, request: dict[str, Any]) -> dict[str, Any]:
        """Perform deterministic unified risk intelligence profiling on a single project observation.

        Reuses the PR-10 UnifiedRiskPredictor to run full fail-closed structural,
        leakage, numeric, and regime validation before generating the intelligence profile.
        """
        serving_result = self.predictor.predict_one(request)
        return self.evaluate_profile_from_serving(serving_result)

    def predict_batch(
        self, requests: Sequence[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Perform deterministic unified risk profiling on a batch of project observations.

        Preserves exact input order, causes no cross-request state mutation, and
        fails closed if any request violates contract rules.
        """
        if not requests:
            return []
        return [self.predict_one(req) for req in requests]
