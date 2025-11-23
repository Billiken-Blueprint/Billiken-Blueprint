"""add_meeting_times_to_sections

Revision ID: 51a911853026
Revises: 5f72efe8f9b3
Create Date: 2025-11-22 19:12:42.359952

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "51a911853026"
down_revision: Union[str, Sequence[str], None] = "5f72efe8f9b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "sections",
        sa.Column("meeting_times", sa.JSON(), nullable=False, server_default="[]"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("sections", "meeting_times")
