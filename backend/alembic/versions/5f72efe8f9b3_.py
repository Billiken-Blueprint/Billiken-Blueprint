"""empty message

Revision ID: 5f72efe8f9b3
Revises: 9a5f1ce95d8d, a1b2c3d4e5f6
Create Date: 2025-11-22 16:33:48.271343

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f72efe8f9b3'
down_revision: Union[str, Sequence[str], None] = ('9a5f1ce95d8d', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
