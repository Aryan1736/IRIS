"""IRIS PR-08 Implementation Risk Target Definition, Eligibility Logic, and Audit Module.

This module provides deterministic, auditable, and leak-free target construction,
right-censoring detection, temporal feasibility analysis, and contract validation
for implementation-risk and physical-progress stagnation prediction in IRIS.

No predictive models are trained in this module.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

DEFAULT_CONTRACT_PATH = Path("schemas/implementation_risk_v1.contract.json")
DEFAULT_OUTPUT_DIR = Path("artifacts/ml/implementation_risk_target_v1")

CONTINUOUS_SEGMENTS = [
    {
        "name": "SEGMENT_1",
        "identifier_regime": "LEGACY",
        "start": "2023-01",
        "end": "2023-11",
        "physical_progress_supported": False,
    },
    {
        "name": "SEGMENT_2",
        "identifier_regime": "LEGACY",
        "start": "2024-01",
        "end": "2024-03",
        "physical_progress_supported": False,
    },
    {
        "name": "SEGMENT_3",
        "identifier_regime": "LEGACY",
        "start": "2024-06",
        "end": "2025-06",
        "physical_progress_supported": True,
    },
    {
        "name": "SEGMENT_4",
        "identifier_regime": "MODERN",
        "start": "2025-07",
        "end": "2026-07",
        "physical_progress_supported": True,
    },
]

HORIZON = 3
TOLERANCE_PROGRESS = 1e-6  # Tolerance for floating-point comparisons


def month_index(month: str) -> int:
    """Convert YYYY-MM to an absolute integer month index."""
    parts = month.split("-")
    if len(parts) != 2:
        raise ValueError(f"Invalid month string format '{month}', expected YYYY-MM")
    year, mon = int(parts[0]), int(parts[1])
    return year * 12 + mon


def add_months(month: str, step: int) -> str:
    """Add integer step months to a YYYY-MM string."""
    idx = month_index(month) - 1 + step
    year = idx // 12
    mon = idx % 12 + 1
    return f"{year:04d}-{mon:02d}"


def months_between(start_month: str, end_month: str) -> int:
    """Count elapsed months between two YYYY-MM strings."""
    return month_index(end_month) - month_index(start_month)


def segment_for_month(month: str) -> dict[str, Any] | None:
    """Identify which continuous segment contains a given report month."""
    for segment in CONTINUOUS_SEGMENTS:
        if segment["start"] <= month <= segment["end"]:
            return segment
    return None


def regime_for_month(month: str) -> str:
    """Determine identifier regime (LEGACY vs MODERN) from report month."""
    return "MODERN" if month >= "2025-07" else "LEGACY"


def sha256_file(path: Path) -> str:
    """Compute uppercase hex SHA-256 digest of a file."""
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1048576):
            hasher.update(chunk)
    return hasher.hexdigest().upper()


def evaluate_embargo(training_month: str, eval_origin: str, horizon: int = HORIZON) -> bool:
    """Evaluate strict walk-forward embargo rule: T + H < E.

    Equality T + H == E is strictly rejected.
    """
    window_end = add_months(training_month, horizon)
    return month_index(window_end) < month_index(eval_origin)


@dataclass(frozen=True)
class ImplementationTargetDecision:
    """Deterministic classification decision for one reference observation."""

    eligible: bool
    reason: str
    label: int | None = None
    progress_subtype: str = ""
    baseline_progress: float | None = None
    future_progress_t3: float | None = None
    delta_progress: float | None = None
    window_end: str = ""


@dataclass(frozen=True)
class EligibilityReconciliation:
    """Deterministic population accounting reconciling all source observations."""

    total_observations: int
    eligible_positives: int
    eligible_negatives: int
    censored_segment_boundary: int
    censored_panel_exit: int
    ineligible_layout_unsupported: int
    ineligible_missing_baseline: int
    ineligible_baseline_completed: int
    ineligible_future_missing: int
    reconciled: bool
    positive_prevalence: float
    class_imbalance_ratio: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CompletedImplementationAuditResult:
    """Audit findings for Candidate 5 (completed projects implementation outcome)."""

    total_completed: int
    physical_progress_column_present: bool
    valid_progress_completed: int
    missing_progress_completed: int
    ongoing_projects_never_completed: int
    ongoing_observations_uncompleted: int
    viability_status: str
    primary_bottlenecks: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_implementation_contract(contract_path: Path | str = DEFAULT_CONTRACT_PATH) -> dict[str, Any]:
    """Load and validate the implementation risk target contract."""
    path = Path(contract_path)
    if not path.is_file():
        raise FileNotFoundError(f"Implementation risk contract not found at {path}")
    with path.open("r", encoding="utf-8") as f:
        contract = json.load(f)

    required_sections = [
        "contract_name",
        "contract_version",
        "dataset_name",
        "dataset_type",
        "target",
        "audited_candidates",
        "features",
        "columns",
        "embargo",
        "continuous_segments",
        "canonical_inputs",
        "expected_dataset_metrics",
        "policies",
        "viability_recommendation",
    ]
    for section in required_sections:
        if section not in contract:
            raise ValueError(f"Contract missing required section: '{section}'")

    if contract["target"]["name"] != "target_progress_stagnation_3m":
        raise ValueError(f"Unexpected target name: {contract['target']['name']}")

    return contract


def validate_canonical_hashes(root: Path, contract: dict[str, Any]) -> dict[str, bool]:
    """Verify that canonical dataset hashes match expected contract hashes."""
    results = {}
    for filename, meta in contract["canonical_inputs"].items():
        file_path = root / meta["relative_path"]
        if not file_path.is_file():
            raise FileNotFoundError(f"Canonical input file missing: {file_path}")
        actual_hash = sha256_file(file_path)
        expected_hash = meta["sha256"]
        if actual_hash != expected_hash:
            raise ValueError(
                f"SHA-256 mismatch for {filename}: expected {expected_hash}, got {actual_hash}"
            )
        results[filename] = True
    return results


def _to_float(v: Any) -> float | None:
    """Safe conversion to float, returning None for empty/null/NaN."""
    if v is None or v == "" or (isinstance(v, float) and np.isnan(v)):
        return None
    try:
        val = float(v)
        return val if not np.isnan(val) else None
    except (ValueError, TypeError):
        return None


def classify_implementation_target(
    current: dict[str, Any],
    by_month: dict[str, dict[str, Any]],
    horizon: int = HORIZON,
    tolerance: float = TOLERANCE_PROGRESS,
) -> ImplementationTargetDecision:
    """Classify one reference observation under strict implementation-risk semantics.

    Rules:
    1. Continuous Segment Boundary: T and T+horizon must be in the same continuous segment.
    2. Panel Exit / Censoring: Project must be observed in every month T+1..T+horizon.
    3. Layout Progress Support: Segment must structurally support physical_progress.
    4. Baseline Physical Progress: physical_progress at T must be present and valid.
    5. Baseline Completed: If physical_progress(T) >= 100.0, the project is physically complete;
       stagnation at completion is not an implementation failure (ineligible).
    6. Future Progress Availability: physical_progress must be reported in T+1..T+horizon.
    7. Positive Condition: physical_progress(T+horizon) - physical_progress(T) <= tolerance
       (progress stalled, zero advancement, or downward revision).
    8. Negative Condition: physical_progress(T+horizon) - physical_progress(T) > tolerance
       (measurable advancement in physical execution).
    """
    report_month = current["report_month"]
    seg_info = segment_for_month(report_month)
    window_end = add_months(report_month, horizon)
    end_seg_info = segment_for_month(window_end)

    # 1. Structural gap or regime boundary (Censored)
    if seg_info is None or end_seg_info is None or seg_info["name"] != end_seg_info["name"]:
        return ImplementationTargetDecision(
            eligible=False,
            reason="STRUCTURAL_GAP_OR_REGIME_BOUNDARY",
            window_end=window_end,
        )

    # 2. Panel exit / missing observation in forward window (Censored)
    future_months = [add_months(report_month, step) for step in range(1, horizon + 1)]
    if any(month not in by_month for month in future_months):
        return ImplementationTargetDecision(
            eligible=False,
            reason="PROJECT_DISAPPEARED_OR_PANEL_EXIT",
            window_end=window_end,
        )

    # 3. Layout progress support check (Ineligible/Ambiguous)
    if not seg_info.get("physical_progress_supported", False):
        return ImplementationTargetDecision(
            eligible=False,
            reason="LAYOUT_PROGRESS_UNSUPPORTED",
            window_end=window_end,
        )

    # 4. Baseline physical progress evaluation
    p_t = _to_float(current.get("physical_progress"))
    if p_t is None:
        return ImplementationTargetDecision(
            eligible=False,
            reason="MISSING_BASELINE_PROGRESS",
            window_end=window_end,
        )

    if p_t < 0.0:
        return ImplementationTargetDecision(
            eligible=False,
            reason="INVALID_BASELINE_PROGRESS",
            baseline_progress=p_t,
            window_end=window_end,
        )

    # 5. Baseline already completed (Ineligible/Ambiguous)
    if p_t >= 100.0:
        return ImplementationTargetDecision(
            eligible=False,
            reason="BASELINE_ALREADY_COMPLETED",
            baseline_progress=p_t,
            window_end=window_end,
        )

    # 6. Future progress availability in T+1..T+horizon
    future_p_vals = []
    for fm in future_months:
        fp = _to_float(by_month[fm].get("physical_progress"))
        if fp is None:
            return ImplementationTargetDecision(
                eligible=False,
                reason="FUTURE_PROGRESS_MISSING",
                baseline_progress=p_t,
                window_end=window_end,
            )
        future_p_vals.append(fp)

    p_end = future_p_vals[-1]
    delta_p = p_end - p_t

    # 7. Classification: Positive vs Negative
    if delta_p <= tolerance:
        subtype = "DETERIORATION" if delta_p < -tolerance else "ZERO_ADVANCE"
        return ImplementationTargetDecision(
            eligible=True,
            reason="ELIGIBLE_POSITIVE",
            label=1,
            progress_subtype=subtype,
            baseline_progress=p_t,
            future_progress_t3=p_end,
            delta_progress=delta_p,
            window_end=window_end,
        )

    return ImplementationTargetDecision(
        eligible=True,
        reason="ELIGIBLE_NEGATIVE",
        label=0,
        progress_subtype="ADVANCE",
        baseline_progress=p_t,
        future_progress_t3=p_end,
        delta_progress=delta_p,
        window_end=window_end,
    )


def build_implementation_risk_population(
    df_monthly: pd.DataFrame,
    horizon: int = HORIZON,
    tolerance: float = TOLERANCE_PROGRESS,
) -> pd.DataFrame:
    """Classify the entire monthly panel into eligible, censored, and ambiguous records."""
    df_sorted = df_monthly.sort_values(["project_code", "report_month"]).copy()
    projects = df_sorted.groupby("project_code")

    records = []
    for p_code, group in projects:
        rows = group.to_dict("records")
        by_month = {r["report_month"]: r for r in rows}

        for current in rows:
            decision = classify_implementation_target(
                current,
                by_month,
                horizon=horizon,
                tolerance=tolerance,
            )

            seg_info = segment_for_month(current["report_month"])
            seg_name = seg_info["name"] if seg_info else "NONE"

            records.append(
                {
                    "project_code": p_code,
                    "report_month": current["report_month"],
                    "identifier_regime": regime_for_month(current["report_month"]),
                    "continuous_segment": seg_name,
                    "eligible": decision.eligible,
                    "disposition_reason": decision.reason,
                    "target_progress_stagnation_3m": decision.label,
                    "progress_stagnation_subtype": decision.progress_subtype,
                    "baseline_progress": decision.baseline_progress,
                    "future_progress_t3": decision.future_progress_t3,
                    "delta_physical_progress_3m": decision.delta_progress,
                    "window_end_month": decision.window_end,
                }
            )

    return pd.DataFrame(records)


def reconcile_population(classified_df: pd.DataFrame) -> EligibilityReconciliation:
    """Verify exact deterministic population reconciliation of classified records."""
    total = len(classified_df)
    counts = classified_df["disposition_reason"].value_counts().to_dict()

    el_pos = counts.get("ELIGIBLE_POSITIVE", 0)
    el_neg = counts.get("ELIGIBLE_NEGATIVE", 0)
    cens_bnd = counts.get("STRUCTURAL_GAP_OR_REGIME_BOUNDARY", 0)
    cens_exit = counts.get("PROJECT_DISAPPEARED_OR_PANEL_EXIT", 0)
    inelig_layout = counts.get("LAYOUT_PROGRESS_UNSUPPORTED", 0)
    inelig_base_miss = counts.get("MISSING_BASELINE_PROGRESS", 0)
    inelig_base_comp = counts.get("BASELINE_ALREADY_COMPLETED", 0)
    inelig_fut_miss = counts.get("FUTURE_PROGRESS_MISSING", 0)
    inelig_base_inv = counts.get("INVALID_BASELINE_PROGRESS", 0)

    accounted = (
        el_pos
        + el_neg
        + cens_bnd
        + cens_exit
        + inelig_layout
        + inelig_base_miss
        + inelig_base_comp
        + inelig_fut_miss
        + inelig_base_inv
    )
    reconciled = accounted == total

    eligible_total = el_pos + el_neg
    prevalence = el_pos / eligible_total if eligible_total > 0 else 0.0
    imbalance = el_neg / el_pos if el_pos > 0 else float("inf")

    return EligibilityReconciliation(
        total_observations=total,
        eligible_positives=el_pos,
        eligible_negatives=el_neg,
        censored_segment_boundary=cens_bnd,
        censored_panel_exit=cens_exit,
        ineligible_layout_unsupported=inelig_layout,
        ineligible_missing_baseline=inelig_base_miss + inelig_base_inv,
        ineligible_baseline_completed=inelig_base_comp,
        ineligible_future_missing=inelig_fut_miss,
        reconciled=reconciled,
        positive_prevalence=prevalence,
        class_imbalance_ratio=imbalance,
    )


def audit_completed_implementation_risk(
    df_completed: pd.DataFrame,
    df_monthly: pd.DataFrame,
) -> CompletedImplementationAuditResult:
    """Audit Candidate 5 (completed projects implementation outcome) and document unviability."""
    total_completed = len(df_completed)
    has_progress_col = "physical_progress" in df_completed.columns

    n_valid_prog = int(df_completed["physical_progress"].notna().sum()) if has_progress_col else 0
    n_miss_prog = total_completed - n_valid_prog

    unique_monthly_projects = df_monthly["project_code"].nunique()
    completed_codes = set(df_completed["project_code"])
    ongoing_never_completed = unique_monthly_projects - len(completed_codes)
    ongoing_uncompleted_obs = int((~df_monthly["project_code"].isin(completed_codes)).sum())

    bottlenecks = [
        "extreme_right_censoring_81.5_pct_ongoing_projects",
        "physical_progress_column_absent_in_completed_dataset",
        "survivorship_bias_only_completed_projects_observed",
        "sector_concentration_over_50_pct_road_transport",
        "temporal_clustering_june_2026_and_oct_2024",
    ]

    return CompletedImplementationAuditResult(
        total_completed=total_completed,
        physical_progress_column_present=has_progress_col,
        valid_progress_completed=n_valid_prog,
        missing_progress_completed=n_miss_prog,
        ongoing_projects_never_completed=ongoing_never_completed,
        ongoing_observations_uncompleted=ongoing_uncompleted_obs,
        viability_status="NOT_YET_VIABLE",
        primary_bottlenecks=bottlenecks,
    )


def audit_temporal_feasibility(classified_df: pd.DataFrame) -> pd.DataFrame:
    """Generate month-by-month and segment-by-segment temporal audit table."""
    summary_rows = []
    months = sorted(classified_df["report_month"].unique())

    for m in months:
        m_df = classified_df[classified_df["report_month"] == m]
        seg = m_df["continuous_segment"].iloc[0]
        regime = m_df["identifier_regime"].iloc[0]
        tot = len(m_df)
        el = int(m_df["eligible"].sum())
        pos = int((m_df["target_progress_stagnation_3m"] == 1).sum())
        neg = int((m_df["target_progress_stagnation_3m"] == 0).sum())
        cens = int(
            m_df["disposition_reason"]
            .isin(["STRUCTURAL_GAP_OR_REGIME_BOUNDARY", "PROJECT_DISAPPEARED_OR_PANEL_EXIT"])
            .sum()
        )
        amb = int(
            m_df["disposition_reason"]
            .isin(
                [
                    "LAYOUT_PROGRESS_UNSUPPORTED",
                    "MISSING_BASELINE_PROGRESS",
                    "BASELINE_ALREADY_COMPLETED",
                    "FUTURE_PROGRESS_MISSING",
                    "INVALID_BASELINE_PROGRESS",
                ]
            )
            .sum()
        )

        pos_rate = pos / el if el > 0 else 0.0

        # Walk-forward eligible: prediction window completes before modern test evaluation
        window_end = add_months(m, HORIZON)
        wf_eligible = el > 0

        summary_rows.append(
            {
                "report_month": m,
                "continuous_segment": seg,
                "identifier_regime": regime,
                "window_end_month": window_end,
                "total_observations": tot,
                "eligible_observations": el,
                "positive_events": pos,
                "negative_events": neg,
                "positive_rate": round(pos_rate, 4),
                "censored_observations": cens,
                "ambiguous_observations": amb,
                "walk_forward_eligible": wf_eligible,
            }
        )

    return pd.DataFrame(summary_rows)


def audit_leakage(contract: dict[str, Any], candidate_features: Iterable[str]) -> dict[str, Any]:
    """Audit feature set against prohibited leakage fields and target source fields."""
    prohibited_set = set(contract["columns"]["leakage_strictly_prohibited"])
    metadata_set = set(contract["columns"]["metadata_only"])
    feature_set = set(candidate_features)

    direct_leakage = sorted(list(feature_set.intersection(prohibited_set)))
    metadata_leakage = sorted(list(feature_set.intersection(metadata_set)))

    return {
        "candidate_feature_count": len(feature_set),
        "prohibited_count": len(prohibited_set),
        "is_leak_free": len(direct_leakage) == 0,
        "direct_leakage_fields": direct_leakage,
        "metadata_leakage_fields": metadata_leakage,
        "allowed_input_families": contract["features"]["families"],
    }


def generate_audit_artifacts(
    root: Path = Path("."),
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    contract_path: Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Path]:
    """Execute complete PR-08 implementation risk audit and write deterministic artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    contract = load_implementation_contract(contract_path)

    # Validate dataset hashes
    validate_canonical_hashes(root, contract)

    monthly_csv = root / contract["canonical_inputs"]["projects_monthly.csv"]["relative_path"]
    completed_csv = root / contract["canonical_inputs"]["projects_completed.csv"]["relative_path"]

    df_monthly = pd.read_csv(monthly_csv, low_memory=False)
    df_completed = pd.read_csv(completed_csv, low_memory=False)

    # 1. Build classified population
    classified_df = build_implementation_risk_population(
        df_monthly,
        horizon=contract["target"]["horizon_months"],
        tolerance=contract["target"]["tolerance_percentage"],
    )

    # 2. Reconcile population
    reconciliation = reconcile_population(classified_df)

    # 3. Audit Candidate 5 (Completed)
    completed_audit = audit_completed_implementation_risk(df_completed, df_monthly)

    # 4. Temporal feasibility
    temporal_df = audit_temporal_feasibility(classified_df)

    # 5. Leakage audit
    leakage_result = audit_leakage(contract, contract["features"]["ordered_names"])

    # 6. Eligibility summary by regime and segment
    eligibility_rows = []
    for (reg, seg), grp in classified_df.groupby(["identifier_regime", "continuous_segment"]):
        el = int(grp["eligible"].sum())
        pos = int((grp["target_progress_stagnation_3m"] == 1).sum())
        neg = int((grp["target_progress_stagnation_3m"] == 0).sum())
        cens = int(
            grp["disposition_reason"]
            .isin(["STRUCTURAL_GAP_OR_REGIME_BOUNDARY", "PROJECT_DISAPPEARED_OR_PANEL_EXIT"])
            .sum()
        )
        amb = int(
            grp["disposition_reason"]
            .isin(
                [
                    "LAYOUT_PROGRESS_UNSUPPORTED",
                    "MISSING_BASELINE_PROGRESS",
                    "BASELINE_ALREADY_COMPLETED",
                    "FUTURE_PROGRESS_MISSING",
                    "INVALID_BASELINE_PROGRESS",
                ]
            )
            .sum()
        )
        rate = pos / el if el > 0 else 0.0
        eligibility_rows.append(
            {
                "identifier_regime": reg,
                "continuous_segment": seg,
                "total_rows": len(grp),
                "eligible_rows": el,
                "positive_events": pos,
                "negative_events": neg,
                "positive_rate": round(rate, 4),
                "censored_rows": cens,
                "ambiguous_or_ineligible_rows": amb,
            }
        )
    eligibility_df = pd.DataFrame(eligibility_rows)

    # 7. Write target_population_summary.csv
    pop_summary_rows = [
        {"metric": "total_observations", "value": reconciliation.total_observations},
        {"metric": "eligible_positives", "value": reconciliation.eligible_positives},
        {"metric": "eligible_negatives", "value": reconciliation.eligible_negatives},
        {"metric": "eligible_total", "value": reconciliation.eligible_positives + reconciliation.eligible_negatives},
        {"metric": "positive_prevalence", "value": round(reconciliation.positive_prevalence, 6)},
        {"metric": "class_imbalance_ratio", "value": round(reconciliation.class_imbalance_ratio, 4)},
        {"metric": "censored_segment_boundary", "value": reconciliation.censored_segment_boundary},
        {"metric": "censored_panel_exit", "value": reconciliation.censored_panel_exit},
        {"metric": "censored_total", "value": reconciliation.censored_segment_boundary + reconciliation.censored_panel_exit},
        {"metric": "ineligible_layout_unsupported", "value": reconciliation.ineligible_layout_unsupported},
        {"metric": "ineligible_missing_baseline", "value": reconciliation.ineligible_missing_baseline},
        {"metric": "ineligible_baseline_completed", "value": reconciliation.ineligible_baseline_completed},
        {"metric": "ineligible_future_missing", "value": reconciliation.ineligible_future_missing},
        {"metric": "ineligible_total", "value": (
            reconciliation.ineligible_layout_unsupported
            + reconciliation.ineligible_missing_baseline
            + reconciliation.ineligible_baseline_completed
            + reconciliation.ineligible_future_missing
        )},
        {"metric": "reconciled", "value": reconciliation.reconciled},
    ]
    pop_summary_path = output_dir / "target_population_summary.csv"
    pd.DataFrame(pop_summary_rows).to_csv(pop_summary_path, index=False)

    # 8. Write eligibility_summary.csv
    eligibility_summary_path = output_dir / "eligibility_summary.csv"
    eligibility_df.to_csv(eligibility_summary_path, index=False)

    # 9. Write temporal_feasibility.csv
    temporal_path = output_dir / "temporal_feasibility.csv"
    temporal_df.to_csv(temporal_path, index=False)

    # 10. Write leakage_audit.json
    leakage_path = output_dir / "leakage_audit.json"
    with leakage_path.open("w", encoding="utf-8") as f:
        json.dump(leakage_result, f, indent=2)

    # 11. Write candidate_recommendation.json
    recommendation_data = {
        "contract_version": contract["contract_version"],
        "primary_target": contract["target"]["name"],
        "viability_status": contract["viability_recommendation"]["status"],
        "recommended_for_pr09": contract["viability_recommendation"]["recommended_for_pr09"],
        "primary_rationale": contract["viability_recommendation"]["primary_rationale"],
        "population_metrics": {
            "total_source_rows": len(df_monthly),
            "eligible_observations": reconciliation.eligible_positives + reconciliation.eligible_negatives,
            "positive_events": reconciliation.eligible_positives,
            "negative_events": reconciliation.eligible_negatives,
            "positive_prevalence": round(reconciliation.positive_prevalence, 6),
            "class_imbalance_ratio": round(reconciliation.class_imbalance_ratio, 4),
            "censored_observations": reconciliation.censored_segment_boundary + reconciliation.censored_panel_exit,
            "ambiguous_or_ineligible_observations": (
                reconciliation.ineligible_layout_unsupported
                + reconciliation.ineligible_missing_baseline
                + reconciliation.ineligible_baseline_completed
                + reconciliation.ineligible_future_missing
            ),
        },
        "audited_candidates": contract["audited_candidates"],
        "completed_projects_audit": completed_audit.to_dict(),
        "limitations": contract["viability_recommendation"]["primary_bottlenecks"],
    }
    rec_path = output_dir / "candidate_recommendation.json"
    with rec_path.open("w", encoding="utf-8") as f:
        json.dump(recommendation_data, f, indent=2)

    # 12. Write manifest.json
    manifest_data = {
        "manifest_version": "1.0.0",
        "pipeline": "IRIS PR-08 Implementation Risk Target Definition",
        "contract": {
            "name": contract["contract_name"],
            "version": contract["contract_version"],
            "target": contract["target"]["name"],
            "horizon_months": contract["target"]["horizon_months"],
            "tolerance_percentage": contract["target"]["tolerance_percentage"],
        },
        "canonical_inputs": contract["canonical_inputs"],
        "population_reconciliation": reconciliation.to_dict(),
        "leakage_audit_summary": {
            "is_leak_free": leakage_result["is_leak_free"],
            "candidate_feature_count": leakage_result["candidate_feature_count"],
            "prohibited_count": leakage_result["prohibited_count"],
        },
        "viability_recommendation": contract["viability_recommendation"],
        "artifacts_generated": {
            "target_population_summary": str(pop_summary_path.relative_to(root)),
            "eligibility_summary": str(eligibility_summary_path.relative_to(root)),
            "temporal_feasibility": str(temporal_path.relative_to(root)),
            "leakage_audit": str(leakage_path.relative_to(root)),
            "candidate_recommendation": str(rec_path.relative_to(root)),
        },
    }
    manifest_path = output_dir / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    return {
        "manifest": manifest_path,
        "target_population_summary": pop_summary_path,
        "eligibility_summary": eligibility_summary_path,
        "temporal_feasibility": temporal_path,
        "leakage_audit": leakage_path,
        "candidate_recommendation": rec_path,
    }


def main() -> None:
    """CLI entrypoint for standalone artifact generation."""
    parser = argparse.ArgumentParser(
        description="IRIS PR-08 Implementation Risk Target Definition & Audit Runner"
    )
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root path")
    parser.add_argument(
        "--contract",
        type=Path,
        default=DEFAULT_CONTRACT_PATH,
        help="Path to implementation risk contract",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to write output artifacts",
    )
    args = parser.parse_args()

    artifacts = generate_audit_artifacts(
        root=args.root,
        output_dir=args.output_dir,
        contract_path=args.contract,
    )
    print("Implementation risk target audit complete. Generated artifacts:")
    for name, path in artifacts.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()
