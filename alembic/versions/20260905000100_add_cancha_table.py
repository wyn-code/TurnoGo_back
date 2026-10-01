"""Add cancha table

Revision ID: 20260905000100
Revises: 20260905000000
Create Date: 2026-09-05 00:01:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260905000100"
down_revision: Union[str, Sequence[str], None] = "20260905000000"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cancha",
        sa.Column("id_cancha", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id_negocio", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_negocio"],
            ["negocio.id_negocio"],
            name="cancha_id_negocio_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id_cancha", name="cancha_pkey"),
    )
    op.create_index("ix_cancha_id_cancha", "cancha", ["id_cancha"])
    op.create_index("ix_cancha_id_negocio", "cancha", ["id_negocio"])


def downgrade() -> None:
    op.drop_index("ix_cancha_id_negocio", table_name="cancha")
    op.drop_index("ix_cancha_id_cancha", table_name="cancha")
    op.drop_table("cancha")
