"""System and dataset metadata services."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.repositories.dataset_metadata_repository import DatasetMetadataRepository
from backend.app.schemas.system import DatasetInfoResponse, DatasetServingStatus


class SystemService:
    """Service handling system-level dataset metadata inspection."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.metadata_repo = DatasetMetadataRepository(db)

    def get_dataset_info(self) -> DatasetInfoResponse:
        """Retrieve current dataset serving information.
        
        Returns an honest NOT_INGESTED payload when the serving layer has not yet been populated.
        """
        active_meta = self.metadata_repo.get_active()
        if (
            active_meta is None
            or active_meta.row_count is None
            or active_meta.row_count == 0
            or not active_meta.covered_months
        ):
            return DatasetInfoResponse(
                status=DatasetServingStatus.NOT_INGESTED,
                dataset_version=None,
                canonical_sha256=None,
                covered_months=[],
                row_count=0,
                unique_projects_count=0,
                source_version_identifier=None,
                ingested_at=None,
            )

        return DatasetInfoResponse(
            status=DatasetServingStatus(active_meta.status),
            dataset_version=active_meta.dataset_version,
            canonical_sha256=active_meta.canonical_sha256,
            covered_months=active_meta.covered_months,
            row_count=active_meta.row_count,
            unique_projects_count=active_meta.unique_projects_count,
            source_version_identifier=active_meta.source_version_identifier,
            ingested_at=active_meta.ingested_at,
        )
