"""rename_user_email_table_to_plural

Revision ID: c256d0279ea6
Revises: 6240656d52f6
Create Date: 2025-03-17 03:16:53.078420

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c256d0279ea6'
down_revision: Union[str, None] = '6240656d52f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename user_email table to user_emails."""
    op.rename_table('user_email', 'user_emails')


def downgrade() -> None:
    """Rename user_emails table back to user_email."""
    op.rename_table('user_emails', 'user_email')