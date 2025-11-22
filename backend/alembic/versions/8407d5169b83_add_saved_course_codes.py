"""add_saved_course_codes

Revision ID: 8407d5169b83
Revises: 6f6c50928852
Create Date: 2025-11-22 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import JSON


# revision identifiers, used by Alembic.
revision: str = '8407d5169b83'
down_revision: Union[str, Sequence[str], None] = '6f6c50928852'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add saved_course_codes column with default empty list
    op.add_column('students', sa.Column('saved_course_codes', JSON, nullable=True, server_default='[]'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('students', 'saved_course_codes')

