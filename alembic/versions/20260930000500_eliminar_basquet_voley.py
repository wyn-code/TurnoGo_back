"""Elimina las categorías sin uso Básquet y Vóley (data migration)

Revision ID: 20260930000500
Revises: 20260930000400
Create Date: 2026-10-01 00:05:00.000000

Aborta (sin borrar nada) si algún negocio usa esas categorías: hay que
reasignarlos antes. downgrade() las recrea como categorías simples; los ids
originales no se pueden garantizar.
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260930000500"
down_revision: Union[str, Sequence[str], None] = "20260930000400"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Mismo SQL que supabase/migrations/20260930000500_eliminar_basquet_voley.sql
UPGRADE_SQL = r"""
do $$
begin
    if exists (
        select 1
        from negocio n
        join categorias c on c.id_categoria = n.id_categoria
        where c.nombre in ('Básquet', 'Basquet', 'Vóley', 'Voley')
    ) then
        raise exception 'Hay negocios en Básquet/Vóley: reasignarlos antes de eliminar las categorías';
    end if;

    delete from categorias where nombre in ('Básquet', 'Basquet', 'Vóley', 'Voley');
end
$$;
"""


def upgrade() -> None:
    op.execute(UPGRADE_SQL)


def downgrade() -> None:
    op.execute(
        """
        insert into categorias (nombre)
        values ('Básquet'), ('Vóley')
        on conflict (nombre) do nothing
        """
    )
