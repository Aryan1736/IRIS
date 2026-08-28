"""Repository for dataset metadata operations."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.dataset_metadata import DatasetMetadata


class DatasetMetadataRepository:
    """Encapsulates database operations for DatasetMetadata."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_active(self) -> DatasetMetadata | None:
        """Fetch the currently active dataset metadata record with row_count > 0."""
        stmt = (
            select(DatasetMetadata)
            .where(
                DatasetMetadata.status == "ACTIVE",
                DatasetMetadata.row_count > 0,
            )
            .order_by(DatasetMetadata.ingested_at.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_version(self, version: str) -> DatasetMetadata | None:
        """Fetch metadata by exact version string."""
        stmt = select(DatasetMetadata).where(DatasetMetadata.dataset_version == version)
        return self.db.execute(stmt).scalar_one_or_none()

    def count(self) -> int:
        """Return count of metadata records."""
        stmt = select(DatasetMetadata)
        return len(self.db.execute(stmt).scalars().all())
