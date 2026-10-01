"""Categorías jerárquicas: agrega categorias.parent_id

Revision ID: 20260930000100
Revises: 20260905000300
Create Date: 2026-09-30 00:01:00.000000

Data migration: "Deportes" pasa a ser categoría padre con sub-categorías.
Los negocios que ya estaban en "Deportes" siguen apuntando al padre (un negocio
puede colgar de un padre o de un hijo), por lo que nada se rompe.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260930000100"
down_revision: Union[str, Sequence[str], None] = "20260905000300"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PADRE = "Deportes"
HIJOS = ("Fútbol", "Pádel", "Tenis", "Básquet", "Vóley")


def upgrade() -> None:
    op.add_column(
        "categorias",
        sa.Column("parent_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "categorias_parent_id_fkey",
        "categorias",
        "categorias",
        ["parent_id"],
        ["id_categoria"],
    )
    op.create_index("ix_categorias_parent_id", "categorias", ["parent_id"])

    # Sub-categorías de Deportes (idempotente: no pisa las que ya existan).
    conn = op.get_bind()
    padre_id = conn.execute(
        sa.text("select id_categoria from categorias where nombre = :n"),
        {"n": PADRE},
    ).scalar()
    if padre_id is None:
        return

    for hijo in HIJOS:
        conn.execute(
            sa.text(
                """
                insert into categorias (nombre, parent_id)
                values (:nombre, :padre)
                on conflict (nombre) do update set parent_id = excluded.parent_id
                """
            ),
            {"nombre": hijo, "padre": padre_id},
        )


def downgrade() -> None:
    conn = op.get_bind()
    # Los negocios de una sub-categoría vuelven al padre antes de borrarla.
    conn.execute(
        sa.text(
            """
            update negocio n
            set id_categoria = c.parent_id
            from categorias c
            where n.id_categoria = c.id_categoria
              and c.parent_id is not null
            """
        )
    )
    conn.execute(sa.text("delete from categorias where parent_id is not null"))

    op.drop_index("ix_categorias_parent_id", table_name="categorias")
    op.drop_constraint("categorias_parent_id_fkey", "categorias", type_="foreignkey")
    op.drop_column("categorias", "parent_id")
