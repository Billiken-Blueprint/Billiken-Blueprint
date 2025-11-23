"""empty message

Revision ID: 849ec7c5735c
Revises: 51a911853026, c332d1611f02
Create Date: 2025-11-23 15:09:50.698469

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '849ec7c5735c'
down_revision: Union[str, Sequence[str], None] = ('51a911853026', 'c332d1611f02')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
