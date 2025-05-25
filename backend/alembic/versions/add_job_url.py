"""add job_url to userEmails

Revision ID: add_job_url
Revises: add_email_id_to_taskruns
Create Date: 2025-05-25 06:17:29.338964

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_job_url'
down_revision: Union[str, None] = 'add_email_id_to_taskruns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # add job_url column to user_emails table
    op.add_column('user_emails', sa.Column('job_url', sa.VARCHAR(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # remove job_url column from user_emails table
    op.drop_column('user_emails', 'job_url')
    # ### end Alembic commands ###
