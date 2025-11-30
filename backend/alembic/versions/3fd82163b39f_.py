"""empty message

Revision ID: 3fd82163b39f
Revises: 849ec7c5735c, f7g8h9i0j1k
Create Date: 2025-11-23 20:47:43.093963

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3fd82163b39f'
down_revision: Union[str, Sequence[str], None] = ('849ec7c5735c', 'f7g8h9i0j1k')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
