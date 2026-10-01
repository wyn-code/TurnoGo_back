"""Add turno id_cancha column

Revision ID: 20260905000200
Revises: 20260905000100
Create Date: 2026-09-05 00:02:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260905000200"
down_revision: Union[str, Sequence[str], None] = "20260905000100"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("turno", sa.Column("id_cancha", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "turno_id_cancha_fkey",
        "turno",
        "cancha",
        ["id_cancha"],
        ["id_cancha"],
        ondelete="SET NULL",
    )
    op.create_index("ix_turno_id_cancha", "turno", ["id_cancha"])

    # Backfill explícito: los turnos preexistentes no pertenecen a ningún espacio.
    op.execute("update turno set id_cancha = null where id_cancha is not null")


def downgrade() -> None:
    op.drop_index("ix_turno_id_cancha", table_name="turno")
    op.drop_constraint("turno_id_cancha_fkey", "turno", type_="foreignkey")
    op.drop_column("turno", "id_cancha")
