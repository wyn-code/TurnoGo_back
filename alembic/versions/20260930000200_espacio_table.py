"""cancha -> espacio (+ numero, descripcion) y espacio por negocio Deportes

Revision ID: 20260930000200
Revises: 20260930000100
Create Date: 2026-09-30 00:02:00.000000

`cancha` ya era el espacio reservable de los negocios "Deportes". En lugar de
duplicar la tabla se renombra a `espacio` (con sus índices y constraints) y se
le agregan `numero` y `descripcion`.

A diferencia del diseño original, `id_negocio` NO es UNIQUE: un negocio
multi-cancha tiene varios espacios.

Data migration: cada negocio de categoría "Deportes" (o sub-categoría) que no
tenga espacios recibe uno con el nombre del negocio.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260930000200"
down_revision: Union[str, Sequence[str], None] = "20260930000100"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("cancha", "espacio")
    op.alter_column("espacio", "id_cancha", new_column_name="id_espacio")

    op.execute("alter index ix_cancha_id_cancha rename to ix_espacio_id_espacio")
    op.execute("alter index ix_cancha_id_negocio rename to idx_espacio_negocio")
    op.execute("alter table espacio rename constraint cancha_pkey to espacio_pkey")
    op.execute(
        "alter table espacio rename constraint cancha_id_negocio_fkey "
        "to fk_espacio_negocio"
    )
    op.execute("alter sequence if exists cancha_id_cancha_seq rename to espacio_id_espacio_seq")

    op.add_column("espacio", sa.Column("numero", sa.Integer(), nullable=True))
    op.add_column("espacio", sa.Column("descripcion", sa.Text(), nullable=True))

    # Numeración correlativa por negocio para los espacios ya existentes.
    op.execute(
        """
        update espacio e
        set numero = r.n
        from (
            select id_espacio,
                   row_number() over (partition by id_negocio order by id_espacio) as n
            from espacio
        ) r
        where e.id_espacio = r.id_espacio
        """
    )

    # Un espacio por cada negocio Deportes (categoría o sub-categoría) sin espacios.
    op.execute(
        """
        insert into espacio (nombre, numero, id_negocio, activo)
        select left(n.nombre, 100), 1, n.id_negocio, true
        from negocio n
        join categorias c on c.id_categoria = n.id_categoria
        where (c.nombre = 'Deportes'
               or c.parent_id in (select id_categoria from categorias where nombre = 'Deportes'))
          and not exists (select 1 from espacio e where e.id_negocio = n.id_negocio)
        """
    )


def downgrade() -> None:
    # Los espacios creados por la data migration quedan como canchas válidas.
    op.drop_column("espacio", "descripcion")
    op.drop_column("espacio", "numero")

    op.execute("alter sequence if exists espacio_id_espacio_seq rename to cancha_id_cancha_seq")
    op.execute(
        "alter table espacio rename constraint fk_espacio_negocio "
        "to cancha_id_negocio_fkey"
    )
    op.execute("alter table espacio rename constraint espacio_pkey to cancha_pkey")
    op.execute("alter index idx_espacio_negocio rename to ix_cancha_id_negocio")
    op.execute("alter index ix_espacio_id_espacio rename to ix_cancha_id_cancha")

    op.alter_column("espacio", "id_espacio", new_column_name="id_cancha")
    op.rename_table("espacio", "cancha")
