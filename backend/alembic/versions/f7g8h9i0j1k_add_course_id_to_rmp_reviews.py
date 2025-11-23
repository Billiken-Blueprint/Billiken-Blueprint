"""add_course_id_to_rmp_reviews

Revision ID: f7g8h9i0j1k
Revises: e5f6a7b8c9d0
Create Date: 2025-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7g8h9i0j1k'
down_revision: Union[str, Sequence[str], None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('rmp_reviews', sa.Column('course_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_rmp_reviews_course_id'), 'rmp_reviews', ['course_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_rmp_reviews_course_id'), table_name='rmp_reviews')
    op.drop_column('rmp_reviews', 'course_id')

