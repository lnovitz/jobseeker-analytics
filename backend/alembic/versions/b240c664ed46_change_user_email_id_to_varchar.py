"""change_user_email_id_to_varchar

Revision ID: b240c664ed46
Revises: 
Create Date: 2025-03-16 02:58:30.325992

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b240c664ed46'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Change user_email.id column from integer to varchar and create composite primary key."""
    # First, drop any constraints that depend on the id column
    op.execute('ALTER TABLE user_email DROP CONSTRAINT IF EXISTS user_email_pkey')
    
    # Change the column type
    op.alter_column('user_email', 'id', 
                    existing_type=sa.INTEGER(), 
                    type_=sa.VARCHAR(255),
                    postgresql_using='id::varchar')
    
    # Add composite primary key constraint
    op.execute('ALTER TABLE user_email ADD PRIMARY KEY (id, user_id)')


def downgrade() -> None:
    """Revert to integer id column with appropriate primary key."""
    # Drop the composite primary key
    op.execute('ALTER TABLE user_email DROP CONSTRAINT IF EXISTS user_email_pkey')
    
    # Change id back to integer (with potential data loss warning if non-numeric ids exist)
    op.alter_column('user_email', 'id',
                    existing_type=sa.VARCHAR(255),
                    type_=sa.INTEGER(),
                    postgresql_using='id::integer')
    
    # Restore original primary key on id only
    op.execute('ALTER TABLE user_email ADD PRIMARY KEY (id)')
