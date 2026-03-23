"""create todos table

Revision ID: 001
Revises:
Create Date: 2026-03-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the todos table."""
    op.create_table(
        "todos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("text", sa.String(200), nullable=False),
        sa.Column("is_complete", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop the todos table."""
    op.drop_table("todos")
