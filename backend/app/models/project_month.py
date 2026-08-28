"""SQLAlchemy model for canonical project-month observations."""

from __future__ import annotations

from sqlalchemy import BigInteger, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base, TimestampMixin


class ProjectMonthObservation(Base, TimestampMixin):
    """Derived serving layer observation representing a single project in one report month.
    
    This model mirrors the 31 canonical and audit fields extracted from PAIMANA Flash Reports.
    Canonical key is (project_code, report_month).
    """

    __tablename__ = "project_month_observations"

    # In SQLite, autoincrement PK must be INTEGER; in PostgreSQL it is BIGINT/BIGSERIAL.
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    # Identity and source labels
    project_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    legacy_ocms_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pmgid: Mapped[str | None] = mapped_column(String(50), nullable=True)
    project_name: Mapped[str] = mapped_column(Text, nullable=False)
    agency: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)
    ministry: Mapped[str | None] = mapped_column(Text, nullable=True)
    sector: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)
    state: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)

    # Parsed dates (represented as YYYY-MM without invented day)
    approval_date: Mapped[str | None] = mapped_column(String(7), nullable=True)
    start_date: Mapped[str | None] = mapped_column(String(7), nullable=True)
    original_completion_date: Mapped[str | None] = mapped_column(String(7), nullable=True)
    revised_completion_date: Mapped[str | None] = mapped_column(String(7), nullable=True)

    # Parsed numerics (costs in Rs crore, physical progress in percentage)
    original_cost: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    revised_cost: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    cumulative_expenditure: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    physical_progress: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)

    # Time dimension (YYYY-MM)
    report_month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)

    # Source representations for audit and reproducibility
    approval_date_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_completion_date_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    revised_completion_date_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_cost_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    revised_cost_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    cumulative_expenditure_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    physical_progress_raw: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Provenance
    source_file: Mapped[str] = mapped_column(Text, nullable=False)
    source_page: Mapped[int] = mapped_column(Integer, nullable=False)
    source_pages: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_row_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_serial_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extraction_method: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("project_code", "report_month", name="uq_project_month_observation"),
        Index("ix_project_month_code_month", "project_code", "report_month"),
    )
