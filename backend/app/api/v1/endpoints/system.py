"""System dataset information endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.system import DatasetInfoResponse
from backend.app.services.system_service import SystemService

router = APIRouter()


@router.get(
    "/system/dataset-info",
    response_model=DatasetInfoResponse,
    summary="Get Active Dataset Serving Information",
    description=(
        "Retrieve lineage, version, canonical SHA-256 hash, and coverage details of the dataset "
        "currently served by the backend. Returns an honest NOT_INGESTED status if the database has not "
        "been populated with a valid non-empty canonical dataset."
    ),
)
def get_dataset_info(
    db: Session = Depends(get_db),
) -> DatasetInfoResponse:
    """Return lineage metadata for the active canonical dataset."""
    service = SystemService(db)
    return service.get_dataset_info()
