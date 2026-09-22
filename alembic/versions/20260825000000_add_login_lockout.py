"""Add login lockout columns to usuarios

Revision ID: 20260825000000
Revises: 20260819000000
Create Date: 2026-08-25 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260825000000"
down_revision: Union[str, Sequence[str], None] = "20260819000000"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column(
            "failed_login_attempts",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "usuarios",
        sa.Column(
            "locked_until",
            sa.DateTime(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("usuarios", "locked_until")
    op.drop_column("usuarios", "failed_login_attempts")
