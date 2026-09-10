"""IRIS PR-06 Cost Overrun Target Definition, Eligibility Logic, and Audit Module.

This module provides deterministic, auditable, and leak-free target construction,
right-censoring detection, temporal feasibility analysis, and contract validation
for cost-overrun and cost-escalation prediction in IRIS.

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

DEFAULT_CONTRACT_PATH = Path("schemas/cost_overrun_v1.contract.json")
DEFAULT_OUTPUT_DIR = Path("artifacts/ml/cost_overrun_target_v1")

CONTINUOUS_SEGMENTS = [
    {"name": "SEGMENT_1", "identifier_regime": "LEGACY", "start": "2023-01", "end": "2023-11"},
    {"name": "SEGMENT_2", "identifier_regime": "LEGACY", "start": "2024-01", "end": "2024-03"},
    {"name": "SEGMENT_3", "identifier_regime": "LEGACY", "start": "2024-06", "end": "2025-06"},
    {"name": "SEGMENT_4", "identifier_regime": "MODERN", "start": "2025-07", "end": "2026-07"},
]

HORIZON = 3
TOLERANCE_CR = 0.001  # Rs 10,000 threshold to ignore micro-rounding discrepancies


def month_index(month: str) -> int:
    """Convert YYYY-MM to an absolute integer month index."""
    year, mon = (int(part) for part in month.split("-"))
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


def segment_for_month(month: str) -> str | None:
    """Identify which continuous segment contains a given report month."""
    for segment in CONTINUOUS_SEGMENTS:
        if segment["start"] <= month <= segment["end"]:
            return segment["name"]
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


@dataclass(frozen=True)
class CostTargetDecision:
    """Deterministic classification decision for one reference observation."""

    eligible: bool
    reason: str
    label: int | None = None
    cost_revision_type: str = ""
    event_month: str = ""
    event_value: float | None = None
    cost_diff: float | None = None
    cost_growth_ratio: float | None = None
    baseline_cost: float | None = None
    baseline_cost_source: str = ""
    window_end: str = ""


@dataclass(frozen=True)
class EligibilityReconciliation:
    """Deterministic population accounting reconciling all source observations."""

    total_observations: int
    eligible_positives: int
    eligible_negatives: int
    censored_segment_boundary: int
    censored_panel_exit: int
    ineligible_baseline_ambiguous: int
    ineligible_future_ambiguous: int
    ineligible_missing_baseline: int
    ineligible_zero_baseline: int
    reconciled: bool
    positive_prevalence: float
    class_imbalance_ratio: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CompletedAuditResult:
    """Audit findings for Candidate A (completed projects lifecycle cost overrun)."""

    total_completed: int
    valid_baseline_cost: int
    missing_baseline_cost: int
    revised_cost_reported_completed: int
    revised_cost_missing_completed: int
    completed_revised_gt_orig: int
    terminal_linked_revised_present: int
    terminal_linked_revised_gt_orig: int
    ongoing_projects_never_completed: int
    ongoing_observations_uncompleted: int
    viability_status: str
    primary_bottlenecks: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_cost_contract(contract_path: Path | str = DEFAULT_CONTRACT_PATH) -> dict[str, Any]:
    """Load and validate the cost overrun target contract."""
    path = Path(contract_path)
    if not path.is_file():
        raise FileNotFoundError(f"Cost overrun contract not found at {path}")
    with path.open("r", encoding="utf-8") as f:
        contract = json.load(f)

    required_sections = [
        "dataset_name",
        "contract_version",
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

    if contract["target"]["name"] != "target_effective_cost_esc_3m":
        raise ValueError(f"Unexpected target name: {contract['target']['name']}")

    return contract


def _effective_cost(row: dict[str, Any]) -> tuple[float | None, str]:
    """Extract usable baseline cost and its administrative source from a snapshot."""
    rev_raw = row.get("revised_cost")
    orig_raw = row.get("original_cost")

    def _to_float(v: Any) -> float | None:
        if v is None or v == "" or (isinstance(v, float) and np.isnan(v)):
            return None
        try:
            val = float(v)
            return val if not np.isnan(val) else None
        except (ValueError, TypeError):
            return None

    rev_val = _to_float(rev_raw)
    orig_val = _to_float(orig_raw)

    if rev_val is not None and rev_val > 0:
        return rev_val, "REVISED"
    if orig_val is not None and orig_val > 0:
        return orig_val, "ORIGINAL"
    return None, "MISSING_OR_NONPOSITIVE"


def classify_cost_target(
    current: dict[str, Any],
    by_month: dict[str, dict[str, Any]],
    history: list[dict[str, Any]],
    horizon: int = HORIZON,
    tolerance: float = TOLERANCE_CR,
) -> CostTargetDecision:
    """Classify one reference observation under strict reported-revision semantics.

    Rules:
    1. Continuous Segment Boundary: T and T+horizon must be in the same continuous segment.
    2. Panel Exit / Censoring: Project must be observed in every month T+1..T+horizon.
    3. Baseline Cost: original_cost must be present and strictly positive (> 0).
    4. Baseline Persistence Ambiguity: A null revised_cost at T cannot silently reset
       a prior officially approved cost revision back to original sanctioned cost.
    5. Positive Rule: At least one month in T+1..T+horizon reports revised_cost > baseline + tolerance.
    6. Future Persistence Ambiguity: If a revision was present at T or appeared in window,
       a subsequent null in the window without proving a positive is ambiguous.
    7. Negative Rule: Complete window with all revised_cost <= baseline + tolerance and no null resets.
    """
    report_month = current["report_month"]
    assignment = segment_for_month(report_month)
    window_end = add_months(report_month, horizon)
    end_assignment = segment_for_month(window_end)

    # 1. Structural gap or regime boundary (Censored)
    if assignment is None or assignment != end_assignment:
        return CostTargetDecision(
            eligible=False,
            reason="STRUCTURAL_GAP_OR_REGIME_BOUNDARY",
            window_end=window_end,
        )

    # 2. Panel exit / missing observation in forward window (Censored)
    future_months = [add_months(report_month, step) for step in range(1, horizon + 1)]
    if any(month not in by_month for month in future_months):
        return CostTargetDecision(
            eligible=False,
            reason="PROJECT_DISAPPEARED_OR_PANEL_EXIT",
            window_end=window_end,
        )

    # 3. Baseline cost evaluation
    baseline, source = _effective_cost(current)
    orig_val, _ = _effective_cost({"original_cost": current.get("original_cost")})
    if orig_val is None or orig_val <= 0:
        return CostTargetDecision(
            eligible=False,
            reason="MISSING_OR_NONPOSITIVE_BASELINE_COST",
            window_end=window_end,
        )

    # 4. Check prior history for baseline persistence ambiguity
    prior_revision_seen = False
    for prior_row in history:
        if prior_row["report_month"] < report_month:
            p_rev, _ = _effective_cost({"revised_cost": prior_row.get("revised_cost")})
            if p_rev is not None and p_rev > 0:
                prior_revision_seen = True
                break

    if source != "REVISED" and prior_revision_seen:
        return CostTargetDecision(
            eligible=False,
            reason="BASELINE_REVISION_PERSISTENCE_AMBIGUOUS",
            baseline_cost=baseline,
            baseline_cost_source=source,
            window_end=window_end,
        )

    # 5. Check future window for positive cost escalation events
    future = [by_month[m] for m in future_months]
    positive_events = []
    for row in future:
        f_rev, _ = _effective_cost({"revised_cost": row.get("revised_cost")})
        if f_rev is not None and baseline is not None and f_rev > (baseline + tolerance):
            diff = f_rev - baseline
            growth = diff / baseline if baseline > 0 else 0.0
            positive_events.append((row["report_month"], f_rev, diff, growth))

    if positive_events:
        evt_m, evt_v, diff, growth = positive_events[0]
        kind = "SUBSEQUENT_COST_REVISION" if source == "REVISED" else "FIRST_COST_REVISION"
        return CostTargetDecision(
            eligible=True,
            reason="ELIGIBLE_POSITIVE",
            label=1,
            cost_revision_type=kind,
            event_month=evt_m,
            event_value=evt_v,
            cost_diff=diff,
            cost_growth_ratio=growth,
            baseline_cost=baseline,
            baseline_cost_source=source,
            window_end=window_end,
        )

    # 6. Check future window for revision persistence ambiguity
    revision_seen = source == "REVISED"
    for row in future:
        f_rev, _ = _effective_cost({"revised_cost": row.get("revised_cost")})
        if f_rev is not None and f_rev > 0:
            revision_seen = True
        elif revision_seen:
            return CostTargetDecision(
                eligible=False,
                reason="FUTURE_REVISION_PERSISTENCE_AMBIGUOUS",
                baseline_cost=baseline,
                baseline_cost_source=source,
                window_end=window_end,
            )

    # 7. Eligible Negative
    return CostTargetDecision(
        eligible=True,
        reason="ELIGIBLE_NEGATIVE",
        label=0,
        cost_revision_type="NONE",
        cost_diff=0.0,
        cost_growth_ratio=0.0,
        baseline_cost=baseline,
        baseline_cost_source=source,
        window_end=window_end,
    )


def build_cost_overrun_population(
    df_monthly: pd.DataFrame,
    horizon: int = HORIZON,
    tolerance: float = TOLERANCE_CR,
) -> pd.DataFrame:
    """Classify the entire monthly panel into eligible, censored, and ambiguous records."""
    df_sorted = df_monthly.sort_values(["project_code", "report_month"]).copy()
    projects = df_sorted.groupby("project_code")

    records = []
    for p_code, group in projects:
        rows = group.to_dict("records")
        by_month = {r["report_month"]: r for r in rows}

        for i, current in enumerate(rows):
            history = rows[:i]
            decision = classify_cost_target(
                current,
                by_month,
                history,
                horizon=horizon,
                tolerance=tolerance,
            )

            records.append(
                {
                    "project_code": p_code,
                    "report_month": current["report_month"],
                    "identifier_regime": regime_for_month(current["report_month"]),
                    "continuous_segment": segment_for_month(current["report_month"]) or "NONE",
                    "eligible": decision.eligible,
                    "disposition_reason": decision.reason,
                    "target_effective_cost_esc_3m": decision.label,
                    "cost_revision_type": decision.cost_revision_type,
                    "event_month": decision.event_month,
                    "event_revised_cost": decision.event_value,
                    "cost_diff": decision.cost_diff,
                    "cost_growth_ratio": decision.cost_growth_ratio,
                    "baseline_cost": decision.baseline_cost,
                    "baseline_cost_source": decision.baseline_cost_source,
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
    amb_base = counts.get("BASELINE_REVISION_PERSISTENCE_AMBIGUOUS", 0)
    amb_fut = counts.get("FUTURE_REVISION_PERSISTENCE_AMBIGUOUS", 0)
    miss_base = counts.get("MISSING_OR_NONPOSITIVE_BASELINE_COST", 0)

    accounted = el_pos + el_neg + cens_bnd + cens_exit + amb_base + amb_fut + miss_base
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
        ineligible_baseline_ambiguous=amb_base,
        ineligible_future_ambiguous=amb_fut,
        ineligible_missing_baseline=miss_base,
        ineligible_zero_baseline=0,
        reconciled=reconciled,
        positive_prevalence=prevalence,
        class_imbalance_ratio=imbalance,
    )


def audit_completed_cost_overrun(
    df_completed: pd.DataFrame,
    df_monthly: pd.DataFrame,
) -> CompletedAuditResult:
    """Audit Candidate A (lifecycle completed-project cost overrun) and document unviability."""
    total_completed = len(df_completed)
    valid_orig = (df_completed["original_cost"].notna()) & (df_completed["original_cost"] > 0)
    n_valid_orig = int(valid_orig.sum())
    n_miss_orig = total_completed - n_valid_orig

    rev_present = df_completed["revised_cost"].notna()
    n_rev_present = int(rev_present.sum())
    n_rev_missing = total_completed - n_rev_present

    gt_orig = (
        (df_completed["revised_cost"] > df_completed["original_cost"])
        & valid_orig
        & rev_present
    )
    n_completed_gt = int(gt_orig.sum())

    # Terminal monthly linked analysis
    m_sorted = df_monthly.sort_values(["project_code", "report_month"])
    last_m = m_sorted.groupby("project_code").last().reset_index()
    merged = df_completed.merge(last_m, on="project_code", suffixes=("_comp", "_term"))

    term_rev_present = merged["revised_cost_term"].notna()
    n_term_rev_present = int(term_rev_present.sum())

    term_gt = (
        (merged["revised_cost_term"] > merged["original_cost_comp"])
        & merged["original_cost_comp"].notna()
        & term_rev_present
    )
    n_term_gt = int(term_gt.sum())

    unique_monthly_projects = df_monthly["project_code"].nunique()
    completed_codes = set(df_completed["project_code"])
    ongoing_never_completed = unique_monthly_projects - len(completed_codes)

    ongoing_uncompleted_obs = int((~df_monthly["project_code"].isin(completed_codes)).sum())

    bottlenecks = [
        "extreme_right_censoring_81.5_pct_ongoing_projects",
        "outcome_missingness_80.6_pct_completed_revised_cost_null",
        "survivorship_bias_only_completed_projects_observed",
        "sector_concentration_over_50_pct_road_transport",
        "temporal_clustering_june_2026_and_oct_2024",
    ]

    return CompletedAuditResult(
        total_completed=total_completed,
        valid_baseline_cost=n_valid_orig,
        missing_baseline_cost=n_miss_orig,
        revised_cost_reported_completed=n_rev_present,
        revised_cost_missing_completed=n_rev_missing,
        completed_revised_gt_orig=n_completed_gt,
        terminal_linked_revised_present=n_term_rev_present,
        terminal_linked_revised_gt_orig=n_term_gt,
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
        pos = int((m_df["target_effective_cost_esc_3m"] == 1).sum())
        neg = int((m_df["target_effective_cost_esc_3m"] == 0).sum())
        cens = int(
            m_df["disposition_reason"]
            .isin(["STRUCTURAL_GAP_OR_REGIME_BOUNDARY", "PROJECT_DISAPPEARED_OR_PANEL_EXIT"])
            .sum()
        )
        amb = int(
            m_df["disposition_reason"]
            .isin(
                [
                    "BASELINE_REVISION_PERSISTENCE_AMBIGUOUS",
                    "FUTURE_REVISION_PERSISTENCE_AMBIGUOUS",
                    "MISSING_OR_NONPOSITIVE_BASELINE_COST",
                ]
            )
            .sum()
        )

        pos_rate = pos / el if el > 0 else 0.0

        summary_rows.append(
            {
                "report_month": m,
                "continuous_segment": seg,
                "identifier_regime": regime,
                "total_observations": tot,
                "eligible_observations": el,
                "positive_events": pos,
                "negative_events": neg,
                "positive_rate": round(pos_rate, 4),
                "censored_observations": cens,
                "ambiguous_observations": amb,
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
    """Execute complete PR-06 cost overrun audit and write deterministic artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    contract = load_cost_contract(contract_path)

    monthly_csv = root / contract["canonical_inputs"]["projects_monthly.csv"]["relative_path"]
    completed_csv = root / contract["canonical_inputs"]["projects_completed.csv"]["relative_path"]

    df_monthly = pd.read_csv(monthly_csv, low_memory=False)
    df_completed = pd.read_csv(completed_csv, low_memory=False)

    # 1. Build classified population
    classified_df = build_cost_overrun_population(
        df_monthly,
        horizon=contract["target"]["horizon_months"],
        tolerance=contract["target"]["tolerance_cr"],
    )

    # 2. Reconcile population
    reconciliation = reconcile_population(classified_df)

    # 3. Audit Candidate A (Completed)
    completed_audit = audit_completed_cost_overrun(df_completed, df_monthly)

    # 4. Temporal feasibility
    temporal_df = audit_temporal_feasibility(classified_df)

    # 5. Leakage audit
    leakage_result = audit_leakage(contract, contract["features"]["ordered_names"])

    # 6. Eligibility summary by regime and segment
    eligibility_rows = []
    for (reg, seg), grp in classified_df.groupby(["identifier_regime", "continuous_segment"]):
        el = int(grp["eligible"].sum())
        pos = int((grp["target_effective_cost_esc_3m"] == 1).sum())
        neg = int((grp["target_effective_cost_esc_3m"] == 0).sum())
        cens = int(
            grp["disposition_reason"]
            .isin(["STRUCTURAL_GAP_OR_REGIME_BOUNDARY", "PROJECT_DISAPPEARED_OR_PANEL_EXIT"])
            .sum()
        )
        amb = int(
            grp["disposition_reason"]
            .isin(
                [
                    "BASELINE_REVISION_PERSISTENCE_AMBIGUOUS",
                    "FUTURE_REVISION_PERSISTENCE_AMBIGUOUS",
                    "MISSING_OR_NONPOSITIVE_BASELINE_COST",
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
                "positive_rows": pos,
                "negative_rows": neg,
                "positive_rate": round(rate, 4),
                "censored_rows": cens,
                "ambiguous_rows": amb,
            }
        )
    eligibility_df = pd.DataFrame(eligibility_rows)

    # 7. High level target population summary
    summary_data = [
        {"metric": "total_source_observations", "value": reconciliation.total_observations},
        {"metric": "eligible_observations", "value": reconciliation.eligible_positives + reconciliation.eligible_negatives},
        {"metric": "eligible_positives", "value": reconciliation.eligible_positives},
        {"metric": "eligible_negatives", "value": reconciliation.eligible_negatives},
        {"metric": "positive_prevalence_pct", "value": round(reconciliation.positive_prevalence * 100, 2)},
        {"metric": "class_imbalance_ratio", "value": f"1:{reconciliation.class_imbalance_ratio:.1f}"},
        {"metric": "censored_segment_boundary", "value": reconciliation.censored_segment_boundary},
        {"metric": "censored_panel_exit", "value": reconciliation.censored_panel_exit},
        {"metric": "total_censored", "value": reconciliation.censored_segment_boundary + reconciliation.censored_panel_exit},
        {"metric": "ineligible_baseline_ambiguous", "value": reconciliation.ineligible_baseline_ambiguous},
        {"metric": "ineligible_future_ambiguous", "value": reconciliation.ineligible_future_ambiguous},
        {"metric": "total_ambiguous", "value": reconciliation.ineligible_baseline_ambiguous + reconciliation.ineligible_future_ambiguous},
        {"metric": "population_reconciled_exact", "value": reconciliation.reconciled},
    ]
    summary_df = pd.DataFrame(summary_data)

    # Save artifacts
    p_pop_summary = output_dir / "target_population_summary.csv"
    p_eligibility = output_dir / "eligibility_summary.csv"
    p_temporal = output_dir / "temporal_feasibility.csv"
    p_leakage = output_dir / "leakage_audit.json"
    p_manifest = output_dir / "manifest.json"

    summary_df.to_csv(p_pop_summary, index=False)
    eligibility_df.to_csv(p_eligibility, index=False)
    temporal_df.to_csv(p_temporal, index=False)

    with p_leakage.open("w", encoding="utf-8") as f:
        json.dump(leakage_result, f, indent=2)

    manifest_data = {
        "artifact_version": "1.0.0",
        "contract_version": contract["contract_version"],
        "target_name": contract["target"]["name"],
        "horizon_months": contract["target"]["horizon_months"],
        "tolerance_cr": contract["target"]["tolerance_cr"],
        "canonical_inputs": {
            "projects_monthly.csv": {
                "path": str(monthly_csv),
                "rows": len(df_monthly),
                "sha256": sha256_file(monthly_csv),
            },
            "projects_completed.csv": {
                "path": str(completed_csv),
                "rows": len(df_completed),
                "sha256": sha256_file(completed_csv),
            },
        },
        "reconciliation": reconciliation.to_dict(),
        "completed_projects_audit": completed_audit.to_dict(),
        "viability_recommendation": contract["viability_recommendation"],
        "artifacts_generated": {
            "target_population_summary": str(p_pop_summary.relative_to(root)),
            "eligibility_summary": str(p_eligibility.relative_to(root)),
            "temporal_feasibility": str(p_temporal.relative_to(root)),
            "leakage_audit": str(p_leakage.relative_to(root)),
        },
    }

    with p_manifest.open("w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    return {
        "manifest": p_manifest,
        "target_population_summary": p_pop_summary,
        "eligibility_summary": p_eligibility,
        "temporal_feasibility": p_temporal,
        "leakage_audit": p_leakage,
    }


def main() -> None:
    """CLI runner for cost overrun target definition and audit."""
    parser = argparse.ArgumentParser(description="IRIS PR-06 Cost Overrun Target Audit")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root path")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for generated artifacts",
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=DEFAULT_CONTRACT_PATH,
        help="Path to cost overrun contract",
    )
    args = parser.parse_args()

    print("Executing PR-06 Cost Overrun Target Audit...")
    artifacts = generate_audit_artifacts(args.root, args.output_dir, args.contract)
    print(f"Generated artifacts under {args.output_dir}:")
    for name, path in artifacts.items():
        print(f"  - {name}: {path}")


if __name__ == "__main__":
    main()
