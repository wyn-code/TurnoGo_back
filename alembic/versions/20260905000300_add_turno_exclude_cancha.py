"""Add turno no-solapamiento por cancha (EXCLUDE GIST)

Revision ID: 20260905000300
Revises: 20260905000200
Create Date: 2026-09-05 00:03:00.000000
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260905000300"
down_revision: Union[str, Sequence[str], None] = "20260905000200"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CONSTRAINT = "ex_turno_no_solapa_por_cancha"

SQL_AGREGAR = f"""
alter table turno
    add constraint {CONSTRAINT}
    exclude using gist (
        id_cancha with =,
        tstzrange(fecha_hora_inicio, fecha_hora_fin, '[)'::text) with &&
    ) where (id_cancha is not null)
"""


def upgrade() -> None:
    # btree_gist habilita el operador de igualdad sobre id_cancha dentro del índice GiST.
    op.execute("create extension if not exists btree_gist")
    op.execute(SQL_AGREGAR)


def downgrade() -> None:
    op.execute(f"alter table turno drop constraint if exists {CONSTRAINT}")
