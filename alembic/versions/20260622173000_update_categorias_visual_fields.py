"""Update categorias visual fields

Revision ID: 20260622173000
Revises:
Create Date: 2026-06-22 17:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260622173000"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "categorias",
        "icono",
        existing_type=sa.String(length=50),
        type_=sa.String(length=500),
        existing_nullable=True,
    )
    op.add_column(
        "categorias",
        sa.Column("descripcion", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("categorias", "descripcion")
    op.alter_column(
        "categorias",
        "icono",
        existing_type=sa.String(length=500),
        type_=sa.String(length=50),
        existing_nullable=True,
    )
