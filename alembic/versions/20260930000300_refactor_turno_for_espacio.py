"""turno: id_cancha -> id_espacio, empleado XOR espacio y exclusiones por recurso

Revision ID: 20260930000300
Revises: 20260930000200
Create Date: 2026-09-30 00:03:00.000000

- Renombra turno.id_cancha -> id_espacio (FK, índice y exclusión incluidos).
- Reemplaza la exclusión global por empleado por una parcial
  (`where id_empleado is not null`), espejo de la de espacio.
- CHECK: un turno no puede tener empleado Y espacio a la vez.

Desvío respecto del diseño original: el CHECK es "como máximo uno" y no "uno y
solo uno", porque existen turnos legítimos sin recurso (negocios sin
empleados). La obligatoriedad de recurso se valida en el backend.

Data migration: los turnos con empleado Y espacio (la app daba prioridad al
espacio) pierden el empleado para cumplir el CHECK. No se asigna espacio a los
turnos de servicios: conservan su empleado.
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260930000300"
down_revision: Union[str, Sequence[str], None] = "20260930000200"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("create extension if not exists btree_gist")

    op.alter_column("turno", "id_cancha", new_column_name="id_espacio")
    op.execute("alter index ix_turno_id_cancha rename to ix_turno_id_espacio")
    op.execute(
        "alter table turno rename constraint turno_id_cancha_fkey to fk_turno_espacio"
    )
    op.execute(
        "alter table turno rename constraint ex_turno_no_solapa_por_cancha "
        "to ex_turno_no_solapa_espacio"
    )

    # Backfill previo al CHECK.
    op.execute(
        "update turno set id_empleado = null "
        "where id_empleado is not null and id_espacio is not null"
    )
    op.execute(
        """
        alter table turno add constraint chk_turno_no_empleado_y_espacio
        check (id_empleado is null or id_espacio is null)
        """
    )

    op.execute("alter table turno drop constraint if exists ex_turno_no_solapa_por_empleado")
    op.execute(
        """
        alter table turno add constraint ex_turno_no_solapa_empleado
        exclude using gist (
            id_empleado with =,
            tstzrange(fecha_hora_inicio, fecha_hora_fin, '[)'::text) with &&
        ) where (id_empleado is not null)
        """
    )


def downgrade() -> None:
    op.execute("alter table turno drop constraint if exists ex_turno_no_solapa_empleado")
    op.execute(
        """
        alter table turno add constraint ex_turno_no_solapa_por_empleado
        exclude using gist (
            id_empleado with =,
            tstzrange(fecha_hora_inicio, fecha_hora_fin, '[)'::text) with &&
        )
        """
    )
    op.execute("alter table turno drop constraint if exists chk_turno_no_empleado_y_espacio")

    op.execute(
        "alter table turno rename constraint ex_turno_no_solapa_espacio "
        "to ex_turno_no_solapa_por_cancha"
    )
    op.execute(
        "alter table turno rename constraint fk_turno_espacio to turno_id_cancha_fkey"
    )
    op.execute("alter index ix_turno_id_espacio rename to ix_turno_id_cancha")
    op.alter_column("turno", "id_espacio", new_column_name="id_cancha")
