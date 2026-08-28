"""SQLAlchemy model for dataset lineage and serving layer metadata."""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class DatasetMetadata(Base):
    """Metadata tracking ingested canonical dataset versions and hashes.
    
    Ensures the backend and frontend can inspect exactly which dataset version,
    hash, row count, and monthly span are currently being served.
    """

    __tablename__ = "dataset_metadata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_version: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    canonical_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    covered_months: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, nullable=False)
    unique_projects_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_version_identifier: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
