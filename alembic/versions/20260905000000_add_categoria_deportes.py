"""Add categoria Deportes

Revision ID: 20260905000000
Revises: 20260825000000
Create Date: 2026-09-05 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260905000000"
down_revision: Union[str, Sequence[str], None] = "20260825000000"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CATEGORIA_DEPORTES = "Deportes"
ICONO = "https://images.unsplash.com/photo-1574629810360-7efbbe195018"
DESCRIPCION = (
    "Canchas, canchetas, campos de fútbol y espacios deportivos "
    "para reservar por horario."
)


def upgrade() -> None:
    op.execute(
        f"""
        insert into categorias (nombre, icono, descripcion)
        values ('{CATEGORIA_DEPORTES}', '{ICONO}', '{DESCRIPCION}')
        on conflict (nombre) do update
        set icono = excluded.icono,
            descripcion = excluded.descripcion
        """
    )


def downgrade() -> None:
    op.execute(f"delete from categorias where nombre = '{CATEGORIA_DEPORTES}'")
