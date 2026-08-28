"""Explicit dataset ingestion CLI for the PAIMANA serving layer.

This CLI reads the canonical dataset CSV and populates the derived PostgreSQL / SQLite
database layer without modifying the source CSV or performing artificial normalization.

ACTIVATION SAFETY GUARD:
A dataset will NOT be marked as 'ACTIVE' unless:
1. The computed SHA-256 matches an explicitly specified --expected-sha256 or accepted handoff hash, OR
2. The --dev / --mark-active flag is explicitly passed for local development/testing.
Otherwise, the dataset is marked as 'INGESTED_UNVERIFIED' to prevent unfinished extractions
from accidentally becoming the active production serving dataset.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from sqlalchemy import insert, update
from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.models.dataset_metadata import DatasetMetadata
from backend.app.models.project_month import ProjectMonthObservation

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
LOGGER = logging.getLogger("paimana.cli.ingest")

# Known accepted combined SHA-256 hashes from docs/HANDOFF.md
ACCEPTED_CANONICAL_HASHES = {
    "FE115E5FE71CC70552669FC4E0ACC2699B14CFE7545A319EEAEAF577E4DB95C3",  # 2024-01..03, 2024-06..2026-07 (46,568 rows)
}


def compute_sha256(file_path: Path) -> str:
    """Compute the SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with file_path.open("rb") as stream:
        while chunk := stream.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest().upper()


def _parse_float(val: str | None) -> float | None:
    if val is None or val.strip() == "":
        return None
    try:
        return float(val.strip())
    except ValueError:
        return None


def _parse_int(val: str | None) -> int | None:
    if val is None or val.strip() == "":
        return None
    try:
        return int(val.strip())
    except ValueError:
        return None


def _parse_str(val: str | None) -> str | None:
    if val is None or val.strip() == "":
        return None
    return val.strip()


def ingest_canonical_csv(
    csv_path: Path,
    session: Session,
    dataset_version: str | None = None,
    expected_sha256: str | None = None,
    is_dev: bool = False,
    clear_existing: bool = False,
    batch_size: int = 1000,
) -> DatasetMetadata:
    """Ingest a canonical CSV into the database serving layer."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Canonical CSV file not found: {csv_path}")

    actual_sha256 = compute_sha256(csv_path)
    LOGGER.info("Computed SHA-256 checksum: %s", actual_sha256)

    # Determine activation status according to activation safety guards
    status = "INGESTED_UNVERIFIED"
    if is_dev:
        status = "ACTIVE"
        LOGGER.info("Dataset marked ACTIVE via explicit --dev flag (development/testing).")
    elif expected_sha256 and expected_sha256.upper() == actual_sha256:
        status = "ACTIVE"
        LOGGER.info("Dataset marked ACTIVE via verified matching expected SHA-256.")
    elif actual_sha256 in ACCEPTED_CANONICAL_HASHES:
        status = "ACTIVE"
        LOGGER.info("Dataset marked ACTIVE matching recognized accepted canonical SHA-256.")
    else:
        LOGGER.warning(
            "Dataset marked INGESTED_UNVERIFIED: SHA-256 was not explicitly accepted. "
            "Use --dev or provide --expected-sha256 to mark as ACTIVE."
        )

    version_label = dataset_version or f"canonical-{csv_path.stem}-{actual_sha256[:8]}"

    # Read and parse records
    records_to_insert: list[dict[str, Any]] = []
    months_set: set[str] = set()
    projects_set: set[str] = set()

    now = datetime.now(timezone.utc)
    start_time = time.perf_counter()

    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        for row_idx, row in enumerate(reader, start=1):
            project_code = row.get("project_code", "").strip()
            report_month = row.get("report_month", "").strip()
            project_name = row.get("project_name", "").strip()

            if not project_code or not report_month:
                LOGGER.warning("Skipping row %d with missing project_code or report_month", row_idx)
                continue

            months_set.add(report_month)
            projects_set.add(project_code)

            record = {
                "project_code": project_code,
                "legacy_ocms_code": _parse_str(row.get("legacy_ocms_code")),
                "pmgid": _parse_str(row.get("pmgid")),
                "project_name": project_name or f"Project {project_code}",
                "agency": _parse_str(row.get("agency")),
                "ministry": _parse_str(row.get("ministry")),
                "sector": _parse_str(row.get("sector")),
                "state": _parse_str(row.get("state")),
                "approval_date": _parse_str(row.get("approval_date")),
                "start_date": _parse_str(row.get("start_date")),
                "original_completion_date": _parse_str(row.get("original_completion_date")),
                "revised_completion_date": _parse_str(row.get("revised_completion_date")),
                "original_cost": _parse_float(row.get("original_cost")),
                "revised_cost": _parse_float(row.get("revised_cost")),
                "cumulative_expenditure": _parse_float(row.get("cumulative_expenditure")),
                "physical_progress": _parse_float(row.get("physical_progress")),
                "report_month": report_month,
                "approval_date_raw": _parse_str(row.get("approval_date_raw")),
                "start_date_raw": _parse_str(row.get("start_date_raw")),
                "original_completion_date_raw": _parse_str(row.get("original_completion_date_raw")),
                "revised_completion_date_raw": _parse_str(row.get("revised_completion_date_raw")),
                "original_cost_raw": _parse_str(row.get("original_cost_raw")),
                "revised_cost_raw": _parse_str(row.get("revised_cost_raw")),
                "cumulative_expenditure_raw": _parse_str(row.get("cumulative_expenditure_raw")),
                "physical_progress_raw": _parse_str(row.get("physical_progress_raw")),
                "source_file": row.get("source_file", csv_path.name),
                "source_page": _parse_int(row.get("source_page")) or 1,
                "source_pages": _parse_str(row.get("source_pages")),
                "source_row_number": _parse_int(row.get("source_row_number")),
                "source_serial_number": _parse_int(row.get("source_serial_number")),
                "extraction_method": row.get("extraction_method", "pdfplumber-lines-v1"),
                "created_at": now,
            }
            records_to_insert.append(record)

    total_rows = len(records_to_insert)
    LOGGER.info("Parsed %d project observations across %d months.", total_rows, len(months_set))

    if total_rows == 0:
        LOGGER.warning("CSV file contains 0 valid project rows; marking status as EMPTY rather than ACTIVE.")
        status = "EMPTY"

    # If clear_existing is True, remove existing observations
    if clear_existing:
        LOGGER.info("Clearing existing observations before reload...")
        from sqlalchemy import delete
        session.execute(delete(ProjectMonthObservation))

    # If this dataset is becoming ACTIVE, mark previous ACTIVE datasets as SUPERSEDED
    if status == "ACTIVE":
        session.execute(
            update(DatasetMetadata)
            .where(DatasetMetadata.status == "ACTIVE")
            .values(status="SUPERSEDED")
        )

    # Insert DatasetMetadata
    metadata = DatasetMetadata(
        dataset_version=version_label,
        canonical_sha256=actual_sha256,
        covered_months=sorted(months_set),
        row_count=total_rows,
        unique_projects_count=len(projects_set),
        source_version_identifier="paimana-export-v1",
        status=status,
        ingested_at=now,
    )
    session.add(metadata)
    session.flush()

    # Bulk insert observations in chunks
    for i in range(0, total_rows, batch_size):
        chunk = records_to_insert[i : i + batch_size]
        session.execute(insert(ProjectMonthObservation), chunk)
        LOGGER.info("Inserted observations %d - %d of %d", i + 1, min(i + batch_size, total_rows), total_rows)

    session.commit()
    elapsed = time.perf_counter() - start_time
    LOGGER.info(
        "Ingestion completed in %.2fs: %d rows inserted (Version: %s, Status: %s).",
        elapsed,
        total_rows,
        version_label,
        status,
    )
    return metadata


def main() -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Ingest canonical PAIMANA CSV dataset into database.")
    parser.add_argument("--csv", type=Path, default=Path("data/processed/projects_monthly.csv"), help="Path to CSV")
    parser.add_argument("--version", type=str, default=None, help="Custom dataset version label")
    parser.add_argument("--expected-sha256", type=str, default=None, help="Expected SHA-256 hash for verification")
    parser.add_argument("--dev", action="store_true", help="Explicitly mark dataset as ACTIVE for development")
    parser.add_argument("--clear-existing", action="store_true", help="Clear existing observations before reloading")
    parser.add_argument("--batch-size", type=int, default=1000, help="Batch insertion size")

    args = parser.parse_args()

    session = SessionLocal()
    try:
        ingest_canonical_csv(
            csv_path=args.csv,
            session=session,
            dataset_version=args.version,
            expected_sha256=args.expected_sha256,
            is_dev=args.dev,
            clear_existing=args.clear_existing,
            batch_size=args.batch_size,
        )
        return 0
    except Exception as exc:
        LOGGER.exception("Ingestion failed: %s", str(exc))
        session.rollback()
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
