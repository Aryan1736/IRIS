"""Initial schema for dataset metadata and project month observations.

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-08-29 03:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create dataset_metadata table
    op.create_table(
        'dataset_metadata',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('dataset_version', sa.String(length=100), nullable=False),
        sa.Column('canonical_sha256', sa.String(length=64), nullable=False),
        sa.Column('covered_months', sa.JSON(), nullable=False),
        sa.Column('row_count', sa.Integer(), nullable=False),
        sa.Column('unique_projects_count', sa.Integer(), nullable=True),
        sa.Column('source_version_identifier', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('ingested_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('dataset_version', name='uq_dataset_metadata_version')
    )

    # 2. Create project_month_observations table
    op.create_table(
        'project_month_observations',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('project_code', sa.String(length=50), nullable=False),
        sa.Column('legacy_ocms_code', sa.String(length=50), nullable=True),
        sa.Column('pmgid', sa.String(length=50), nullable=True),
        sa.Column('project_name', sa.Text(), nullable=False),
        sa.Column('agency', sa.Text(), nullable=True),
        sa.Column('ministry', sa.Text(), nullable=True),
        sa.Column('sector', sa.Text(), nullable=True),
        sa.Column('state', sa.Text(), nullable=True),
        sa.Column('approval_date', sa.String(length=7), nullable=True),
        sa.Column('start_date', sa.String(length=7), nullable=True),
        sa.Column('original_completion_date', sa.String(length=7), nullable=True),
        sa.Column('revised_completion_date', sa.String(length=7), nullable=True),
        sa.Column('original_cost', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('revised_cost', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('cumulative_expenditure', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('physical_progress', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('report_month', sa.String(length=7), nullable=False),
        sa.Column('approval_date_raw', sa.Text(), nullable=True),
        sa.Column('start_date_raw', sa.Text(), nullable=True),
        sa.Column('original_completion_date_raw', sa.Text(), nullable=True),
        sa.Column('revised_completion_date_raw', sa.Text(), nullable=True),
        sa.Column('original_cost_raw', sa.Text(), nullable=True),
        sa.Column('revised_cost_raw', sa.Text(), nullable=True),
        sa.Column('cumulative_expenditure_raw', sa.Text(), nullable=True),
        sa.Column('physical_progress_raw', sa.Text(), nullable=True),
        sa.Column('source_file', sa.Text(), nullable=False),
        sa.Column('source_page', sa.Integer(), nullable=False),
        sa.Column('source_pages', sa.Text(), nullable=True),
        sa.Column('source_row_number', sa.Integer(), nullable=True),
        sa.Column('source_serial_number', sa.Integer(), nullable=True),
        sa.Column('extraction_method', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_code', 'report_month', name='uq_project_month_observation')
    )

    op.create_index('ix_project_month_observations_project_code', 'project_month_observations', ['project_code'])
    op.create_index('ix_project_month_observations_report_month', 'project_month_observations', ['report_month'])
    op.create_index('ix_project_month_observations_agency', 'project_month_observations', ['agency'])
    op.create_index('ix_project_month_observations_sector', 'project_month_observations', ['sector'])
    op.create_index('ix_project_month_observations_state', 'project_month_observations', ['state'])
    op.create_index('ix_project_month_code_month', 'project_month_observations', ['project_code', 'report_month'])


def downgrade() -> None:
    op.drop_index('ix_project_month_code_month', table_name='project_month_observations')
    op.drop_index('ix_project_month_observations_state', table_name='project_month_observations')
    op.drop_index('ix_project_month_observations_sector', table_name='project_month_observations')
    op.drop_index('ix_project_month_observations_agency', table_name='project_month_observations')
    op.drop_index('ix_project_month_observations_report_month', table_name='project_month_observations')
    op.drop_index('ix_project_month_observations_project_code', table_name='project_month_observations')
    op.drop_table('project_month_observations')
    op.drop_table('dataset_metadata')
