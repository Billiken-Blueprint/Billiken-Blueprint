"""add_rmp_reviews_table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-23 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import JSON


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('rmp_reviews',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('instructor_id', sa.Integer(), nullable=False),
        sa.Column('course', sa.String(), nullable=True),
        sa.Column('quality', sa.Float(), nullable=False),
        sa.Column('difficulty', sa.Float(), nullable=True),
        sa.Column('comment', sa.String(), nullable=False),
        sa.Column('would_take_again', sa.Boolean(), nullable=True),
        sa.Column('grade', sa.String(), nullable=True),
        sa.Column('attendance', sa.String(), nullable=True),
        sa.Column('tags', JSON, nullable=False, server_default='[]'),
        sa.Column('review_date', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rmp_reviews_instructor_id'), 'rmp_reviews', ['instructor_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_rmp_reviews_instructor_id'), table_name='rmp_reviews')
    op.drop_table('rmp_reviews')

