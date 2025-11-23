"""add_additional_fields_to_ratings

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2025-11-23 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('ratings', sa.Column('difficulty', sa.Float(), nullable=True))
    op.add_column('ratings', sa.Column('would_take_again', sa.Boolean(), nullable=True))
    op.add_column('ratings', sa.Column('grade', sa.String(), nullable=True))
    op.add_column('ratings', sa.Column('attendance', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('ratings', 'attendance')
    op.drop_column('ratings', 'grade')
    op.drop_column('ratings', 'would_take_again')
    op.drop_column('ratings', 'difficulty')

