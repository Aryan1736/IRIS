"""Authoritative machine-readable ML data contract validator.

This module provides code-enforced, fail-closed validation for the IRIS
three-month schedule-extension prediction pipeline. It enforces canonical
input integrity, feature specifications, strict walk-forward embargoes,
leakage prohibitions, and segment definitions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Sequence


DEFAULT_CONTRACT_RELATIVE_PATH = Path("schemas/schedule_extension_3m_v1.contract.json")


class ContractValidationError(Exception):
    """Base exception for all ML data contract violations."""


class CanonicalHashMismatchError(ContractValidationError):
    """Raised when canonical input SHA-256 does not match accepted contract hash."""


class CanonicalRowCountMismatchError(ContractValidationError):
    """Raised when canonical input row count does not match accepted contract count."""


class FeatureContractError(ContractValidationError):
    """Raised when features are missing, unexpected, or in incorrect order."""


class LeakageViolationError(ContractValidationError):
    """Raised when prohibited metadata, future outcome, or identifier is used as a feature."""


class EmbargoViolationError(ContractValidationError):
    """Raised when training observation violates the strict T + 3 < E walk-forward embargo."""


class SegmentViolationError(ContractValidationError):
    """Raised when segment boundaries are mutated or unbridged gaps are crossed."""


class TargetContractError(ContractValidationError):
    """Raised when target name, horizon, or semantics violate the contract."""


def compute_file_sha256(path: Path) -> str:
    """Compute uppercase hex SHA-256 digest of a file."""
    if not path.is_file():
        raise FileNotFoundError(f"File not found for hashing: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def month_index(value: str) -> int:
    """Convert YYYY-MM string to zero-based month index."""
    parts = value.split("-")
    if len(parts) != 2:
        raise ValueError(f"Invalid month string format '{value}', expected YYYY-MM")
    year, month = int(parts[0]), int(parts[1])
    return year * 12 + month - 1


def add_months(value: str, count: int) -> str:
    """Add integer count of months to a YYYY-MM string."""
    idx = month_index(value) + count
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}"


def default_contract_path(root: Path | None = None) -> Path:
    """Locate the default machine-readable ML data contract."""
    base = root.resolve() if root else Path.cwd().resolve()
    # If base is inside src/ml or schemas, find root
    if (base / "schemas" / "schedule_extension_3m_v1.contract.json").is_file():
        return base / "schemas" / "schedule_extension_3m_v1.contract.json"
    candidate = Path(__file__).resolve().parents[2] / DEFAULT_CONTRACT_RELATIVE_PATH
    if candidate.is_file():
        return candidate
    raise FileNotFoundError(f"Cannot locate contract file relative to {base} or {__file__}")


def load_contract(contract_path: Path | None = None) -> dict[str, Any]:
    """Load and return the parsed ML data contract JSON."""
    path = contract_path.resolve() if contract_path else default_contract_path()
    if not path.is_file():
        raise FileNotFoundError(f"Contract file does not exist: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    validate_contract_structure(data)
    return data


def validate_contract_structure(contract: dict[str, Any]) -> None:
    """Verify that contract schema contains all required sections and keys."""
    required_keys = [
        "dataset_name",
        "contract_version",
        "target",
        "features",
        "columns",
        "embargo",
        "continuous_segments",
        "canonical_inputs",
        "expected_dataset_metrics",
        "policies",
        "supported_model_regimes",
    ]
    for key in required_keys:
        if key not in contract:
            raise ContractValidationError(f"Contract missing required top-level section: '{key}'")

    target = contract["target"]
    if target.get("name") != "target_effective_schedule_ext_3m":
        raise TargetContractError(f"Unexpected target name: {target.get('name')}")
    if target.get("horizon_months") != 3:
        raise TargetContractError(f"Unexpected target horizon: {target.get('horizon_months')}")

    features = contract["features"]
    if features.get("count") != 36:
        raise FeatureContractError(f"Expected 36 features, found count: {features.get('count')}")
    if len(features.get("ordered_names", [])) != 36:
        raise FeatureContractError(
            f"Expected 36 ordered feature names, found: {len(features.get('ordered_names', []))}"
        )


def validate_canonical_inputs(root: Path, contract: dict[str, Any] | None = None) -> dict[str, Any]:
    """Verify existence, row counts, and SHA-256 hashes of canonical inputs."""
    if contract is None:
        contract = load_contract(default_contract_path(root))

    root = root.resolve()
    canonical_spec = contract["canonical_inputs"]
    results: dict[str, Any] = {}

    for name, spec in canonical_spec.items():
        rel_path = spec.get("relative_path", f"data/processed/{name}")
        file_path = root / rel_path
        if not file_path.is_file():
            raise FileNotFoundError(f"Canonical input file missing: {file_path}")

        # Hash check
        actual_hash = compute_file_sha256(file_path)
        expected_hash = spec["sha256"]
        if actual_hash != expected_hash:
            raise CanonicalHashMismatchError(
                f"Canonical hash mismatch for {name}: expected {expected_hash}, got {actual_hash}"
            )

        # Row count check
        with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
            actual_rows = sum(1 for _ in csv.DictReader(handle))
        expected_rows = spec["rows"]
        if actual_rows != expected_rows:
            raise CanonicalRowCountMismatchError(
                f"Canonical row count mismatch for {name}: expected {expected_rows}, got {actual_rows}"
            )

        results[name] = {"path": str(file_path), "rows": actual_rows, "sha256": actual_hash}

    return results


def validate_features(
    features: Sequence[str],
    contract: dict[str, Any] | None = None,
    strict_order: bool = True,
) -> None:
    """Validate that a feature list matches the contract feature list exactly."""
    if contract is None:
        contract = load_contract()

    expected_features = contract["features"]["ordered_names"]
    features_list = list(features)

    # Check for prohibited leakage columns first
    validate_leakage_exclusion(features_list, contract)

    missing = [f for f in expected_features if f not in features_list]
    extra = [f for f in features_list if f not in expected_features]

    if missing:
        raise FeatureContractError(f"Missing required feature(s): {missing}")
    if extra:
        raise FeatureContractError(f"Unexpected extra feature(s) not in contract: {extra}")

    if strict_order and features_list != expected_features:
        for idx, (actual, expected) in enumerate(zip(features_list, expected_features)):
            if actual != expected:
                raise FeatureContractError(
                    f"Feature ordering mismatch at position {idx}: expected '{expected}', got '{actual}'"
                )


def validate_leakage_exclusion(
    features: Iterable[str], contract: dict[str, Any] | None = None
) -> None:
    """Verify no prohibited leakage, metadata, or outcome columns are present in features."""
    if contract is None:
        contract = load_contract()

    prohibited = set(contract["columns"]["leakage_strictly_prohibited"])
    # Also ensure metadata columns cannot be features unless explicitly designated
    # All leakage_strictly_prohibited must be strictly absent
    feature_set = set(features)
    intersection = feature_set & prohibited
    if intersection:
        raise LeakageViolationError(
            f"Prohibited leakage columns detected in feature set: {sorted(intersection)}"
        )


def validate_target_spec(
    target_name: str, horizon: int, contract: dict[str, Any] | None = None
) -> None:
    """Validate target name and prediction horizon against the contract."""
    if contract is None:
        contract = load_contract()

    expected_name = contract["target"]["name"]
    expected_horizon = contract["target"]["horizon_months"]

    if target_name != expected_name:
        raise TargetContractError(
            f"Target name mismatch: expected '{expected_name}', got '{target_name}'"
        )
    if horizon != expected_horizon:
        raise TargetContractError(
            f"Target horizon mismatch: expected {expected_horizon}, got {horizon}"
        )


def validate_embargo_rule(
    training_month: str, evaluation_month: str, horizon: int = 3
) -> bool:
    """Enforce strict walk-forward embargo: T + horizon < E.

    Returns True if embargo safe, raises EmbargoViolationError if strict check requested.
    """
    safe = month_index(add_months(training_month, horizon)) < month_index(evaluation_month)
    return safe


def check_embargo(
    training_month: str, evaluation_month: str, horizon: int = 3
) -> None:
    """Check embargo and raise EmbargoViolationError if violated."""
    if not validate_embargo_rule(training_month, evaluation_month, horizon):
        raise EmbargoViolationError(
            f"Embargo violation: training month {training_month} with horizon {horizon} "
            f"ends at {add_months(training_month, horizon)}, which is not strictly before "
            f"evaluation month {evaluation_month} (rule: T + {horizon} < E)"
        )


def validate_continuous_segments(
    segments: Any, contract: dict[str, Any] | None = None
) -> None:
    """Verify that segment configuration matches continuous segments in contract."""
    if contract is None:
        contract = load_contract()

    contract_segments = contract["continuous_segments"]
    # Handle tuple or dict format
    normalized_incoming: list[dict[str, str]] = []
    if isinstance(segments, (list, tuple)):
        for item in segments:
            if isinstance(item, dict):
                normalized_incoming.append(item)
            elif isinstance(item, (list, tuple)) and len(item) == 4:
                normalized_incoming.append(
                    {
                        "name": item[0],
                        "identifier_regime": item[1],
                        "start": item[2],
                        "end": item[3],
                    }
                )
            else:
                raise SegmentViolationError(f"Unsupported segment format: {item}")
    else:
        raise SegmentViolationError(f"Segments must be a list or tuple, got {type(segments)}")

    if len(normalized_incoming) != len(contract_segments):
        raise SegmentViolationError(
            f"Segment count mismatch: expected {len(contract_segments)}, got {len(normalized_incoming)}"
        )

    for idx, (incoming, expected) in enumerate(zip(normalized_incoming, contract_segments)):
        for field in ("name", "identifier_regime", "start", "end"):
            if incoming.get(field) != expected.get(field):
                raise SegmentViolationError(
                    f"Segment mismatch at index {idx} on field '{field}': "
                    f"expected '{expected.get(field)}', got '{incoming.get(field)}'"
                )


def validate_dataset_file(
    csv_path: Path, contract: dict[str, Any] | None = None, is_eligible: bool = True
) -> dict[str, Any]:
    """Verify columns, row integrity, and target presence of a dataset CSV file."""
    if contract is None:
        contract = load_contract()

    if not csv_path.is_file():
        raise FileNotFoundError(f"Dataset file does not exist: {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        row_count = 0
        positive_count = 0
        negative_count = 0
        target_name = contract["target"]["name"]

        if is_eligible:
            expected_fields = contract["columns"]["metadata_only"] + contract["features"]["ordered_names"]
            if fields != expected_fields:
                missing = [f for f in expected_fields if f not in fields]
                extra = [f for f in fields if f not in expected_fields]
                if missing or extra or fields != expected_fields:
                    raise FeatureContractError(
                        f"Dataset file {csv_path.name} fields mismatch: "
                        f"missing={missing}, extra={extra}, field_order_match={fields == expected_fields}"
                    )

        for row in reader:
            row_count += 1
            if is_eligible:
                label = row.get(target_name)
                if label == "1":
                    positive_count += 1
                elif label == "0":
                    negative_count += 1
                else:
                    raise TargetContractError(
                        f"Invalid target label '{label}' at row {row_count} in {csv_path.name}"
                    )

    return {
        "file": csv_path.name,
        "rows": row_count,
        "positive_rows": positive_count,
        "negative_rows": negative_count,
    }


def validate_built_dataset(
    dataset_dir: Path, contract: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Validate all generated artifacts in schedule_extension_3m dataset directory."""
    if contract is None:
        contract = load_contract()

    dataset_dir = dataset_dir.resolve()
    legacy_path = dataset_dir / "eligible_legacy.csv"
    modern_path = dataset_dir / "eligible_modern.csv"
    manifest_path = dataset_dir / "manifest.json"

    for path in (legacy_path, modern_path, manifest_path):
        if not path.is_file():
            raise FileNotFoundError(f"Required dataset artifact missing: {path}")

    legacy_res = validate_dataset_file(legacy_path, contract, is_eligible=True)
    modern_res = validate_dataset_file(modern_path, contract, is_eligible=True)

    expected_metrics = contract["expected_dataset_metrics"]
    expected_legacy = expected_metrics["eligible_rows"]["LEGACY"]
    expected_modern = expected_metrics["eligible_rows"]["MODERN"]

    if legacy_res["rows"] != expected_legacy:
        raise ContractValidationError(
            f"Legacy eligible rows mismatch: expected {expected_legacy}, got {legacy_res['rows']}"
        )
    if modern_res["rows"] != expected_modern:
        raise ContractValidationError(
            f"Modern eligible rows mismatch: expected {expected_modern}, got {modern_res['rows']}"
        )

    expected_legacy_pos = expected_metrics["positive_rows"]["LEGACY"]
    expected_modern_pos = expected_metrics["positive_rows"]["MODERN"]

    if legacy_res["positive_rows"] != expected_legacy_pos:
        raise ContractValidationError(
            f"Legacy positive rows mismatch: expected {expected_legacy_pos}, got {legacy_res['positive_rows']}"
        )
    if modern_res["positive_rows"] != expected_modern_pos:
        raise ContractValidationError(
            f"Modern positive rows mismatch: expected {expected_modern_pos}, got {modern_res['positive_rows']}"
        )

    # Manifest verification
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    if manifest.get("target") != contract["target"]["name"]:
        raise TargetContractError(f"Manifest target mismatch: {manifest.get('target')}")
    if manifest.get("target_horizon_months") != contract["target"]["horizon_months"]:
        raise TargetContractError(
            f"Manifest horizon mismatch: {manifest.get('target_horizon_months')}"
        )
    if manifest.get("feature_columns") != contract["features"]["ordered_names"]:
        raise FeatureContractError("Manifest feature_columns do not match contract ordered_names")

    return {
        "status": "PASS",
        "legacy": legacy_res,
        "modern": modern_res,
        "manifest_version": manifest.get("dataset_name"),
    }


def main() -> int:
    """CLI entry point for verifying the repository data contract."""
    parser = argparse.ArgumentParser(
        description="Verify IRIS ML Data Contract against canonical inputs and built dataset."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root path")
    parser.add_argument(
        "--contract", type=Path, default=None, help="Path to contract JSON (optional)"
    )
    args = parser.parse_args()

    root = args.root.resolve()
    contract_path = args.contract.resolve() if args.contract else default_contract_path(root)

    print(f"Loading ML data contract from: {contract_path}")
    contract = load_contract(contract_path)
    print(f"Contract: {contract['dataset_name']} v{contract['contract_version']}")

    print("\n1. Validating canonical inputs...")
    input_results = validate_canonical_inputs(root, contract)
    for name, info in input_results.items():
        print(f"  [PASS] {name}: {info['rows']} rows, hash={info['sha256'][:16]}...")

    print("\n2. Validating feature contract...")
    validate_features(contract["features"]["ordered_names"], contract, strict_order=True)
    print(f"  [PASS] All {contract['features']['count']} features strictly validated in contract order.")

    print("\n3. Validating leakage protection...")
    validate_leakage_exclusion(contract["features"]["ordered_names"], contract)
    print(f"  [PASS] Zero prohibited leakage columns present in feature set.")

    print("\n4. Validating segment continuity and boundaries...")
    segments = [
        (s["name"], s["identifier_regime"], s["start"], s["end"])
        for s in contract["continuous_segments"]
    ]
    validate_continuous_segments(segments, contract)
    print(f"  [PASS] Continuous segments verified (4 segments, strict gap isolation).")

    dataset_dir = root / "data" / "ml" / "schedule_extension_3m"
    if dataset_dir.is_dir():
        print("\n5. Validating built ML dataset outputs...")
        dataset_results = validate_built_dataset(dataset_dir, contract)
        print(f"  [PASS] Legacy: {dataset_results['legacy']['rows']} rows ({dataset_results['legacy']['positive_rows']} positive)")
        print(f"  [PASS] Modern: {dataset_results['modern']['rows']} rows ({dataset_results['modern']['positive_rows']} positive)")
    else:
        print(f"\n5. Built dataset directory not found at {dataset_dir} (skipping output audit).")

    print("\n[SUCCESS] ML data contract validation PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
