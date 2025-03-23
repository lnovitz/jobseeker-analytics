"""add_job_title_column

Revision ID: 6240656d52f6
Revises: b240c664ed46
Create Date: 2025-03-16 21:31:17.486275

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6240656d52f6'
down_revision: Union[str, None] = 'b240c664ed46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add job_title column to the relevant table."""
    op.add_column('user_email', sa.Column('job_title', sa.String(255), nullable=True))



def downgrade() -> None:
    """Remove job_title column."""
    op.drop_column('user_email', 'job_title')