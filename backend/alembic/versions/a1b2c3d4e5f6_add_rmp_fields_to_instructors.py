"""add_rmp_fields_to_instructors

Revision ID: a1b2c3d4e5f6
Revises: 8407d5169b83
Create Date: 2025-11-22 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '6f6c50928852'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('instructors', sa.Column('rmp_rating', sa.Float(), nullable=True))
    op.add_column('instructors', sa.Column('rmp_num_ratings', sa.Integer(), nullable=True))
    op.add_column('instructors', sa.Column('rmp_url', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('instructors', 'rmp_url')
    op.drop_column('instructors', 'rmp_num_ratings')
    op.drop_column('instructors', 'rmp_rating')

