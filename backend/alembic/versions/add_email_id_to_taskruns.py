"""add email_id to TaskRuns

Revision ID: add_email_id_to_taskruns
Revises: add_task_id_column
Create Date: 2025-05-25 05:58:35.591095

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_email_id_to_taskruns'
down_revision: Union[str, None] = 'add_task_id_column'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # add email_id column to processing_task_runs table
    op.add_column('processing_task_runs', sa.Column('email_id', sa.VARCHAR(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # remove email_id column from processing_task_runs table
    op.drop_column('processing_task_runs', 'email_id')
    # ### end Alembic commands ###
