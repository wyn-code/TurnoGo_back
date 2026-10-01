"""Consolida las categorías deportivas bajo "Deportes" (data migration)

Revision ID: 20260930000400
Revises: 20260930000300
Create Date: 2026-10-01 00:00:00.000000

Estado real que corrige: "Canchas de Futbol" / "Canchas de Padle" eran categorías
raíz sueltas con negocios, y la migración 20260930000100 había agregado
"Fútbol"/"Pádel" como hijas vacías de Deportes (duplicadas).

Resultado: Deportes -> Cancha de Futbol, Cancha de Padel, Cancha de Tenis.
- Se conservan (renombran y reubican) las categorías que ya tienen negocios;
  las duplicadas se fusionan en ellas (sus negocios se reasignan) y se borran.
- Se corrige el typo "Padle". Básquet y Vóley quedan como categorías simples.
- Los negocios que pasan a Deportes y no tienen espacios reciben uno, para que
  puedan seguir reservándose.

Idempotente. downgrade() restaura la estructura previa, no los datos borrados:
vuelve a crear Fútbol/Pádel vacías.
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260930000400"
down_revision: Union[str, Sequence[str], None] = "20260930000300"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Mismo SQL que supabase/migrations/20260930000400_consolidar_categorias_deportes.sql
UPGRADE_SQL = r"""
do $$
declare
    padre integer;
    spec record;
    otro record;
    target integer;
    nombres text[];
begin
    select id_categoria into padre from categorias where nombre = 'Deportes';
    if padre is null then
        insert into categorias (nombre, descripcion)
        values ('Deportes', 'Canchas, canchetas, campos de fútbol y espacios deportivos para reservar por horario.')
        returning id_categoria into padre;
    end if;

    for spec in
        select * from (values
            ('Cancha de Futbol', array['Canchas de Futbol', 'Fútbol']),
            ('Cancha de Padel',  array['Canchas de Padle', 'Canchas de Padel', 'Pádel']),
            ('Cancha de Tenis',  array['Tenis'])
        ) as t(nuevo, legado)
    loop
        nombres := array[spec.nuevo] || spec.legado;
        target := null;

        -- La primera que exista (por prioridad) se conserva; las demás se fusionan en ella.
        for otro in
            select c.id_categoria, c.icono, c.descripcion
            from categorias c
            join unnest(nombres) with ordinality u(n, o) on u.n = c.nombre
            order by u.o
        loop
            if target is null then
                target := otro.id_categoria;
            else
                update negocio set id_categoria = target where id_categoria = otro.id_categoria;
                update categorias
                set icono = coalesce(icono, otro.icono),
                    descripcion = coalesce(descripcion, otro.descripcion)
                where id_categoria = target;
                delete from categorias where id_categoria = otro.id_categoria;
            end if;
        end loop;

        if target is null then
            insert into categorias (nombre, parent_id) values (spec.nuevo, padre);
        else
            update categorias set nombre = spec.nuevo, parent_id = padre where id_categoria = target;
        end if;
    end loop;

    -- Básquet y Vóley quedan como categorías simples (no son canchas de Deportes).
    update categorias set parent_id = null
    where nombre in ('Básquet', 'Vóley') and parent_id = padre;

    -- Los negocios que pasaron a Deportes reservan por espacio: uno por negocio si no tienen.
    insert into espacio (nombre, numero, id_negocio, activo)
    select left(n.nombre, 100), 1, n.id_negocio, true
    from negocio n
    join categorias c on c.id_categoria = n.id_categoria
    where (c.id_categoria = padre or c.parent_id = padre)
      and not exists (select 1 from espacio e where e.id_negocio = n.id_negocio);
end
$$;

"""


def upgrade() -> None:
    op.execute(UPGRADE_SQL)


def downgrade() -> None:
    op.execute(
        r"""
        do $$
        declare padre integer;
        begin
            select id_categoria into padre from categorias where nombre = 'Deportes';
            if padre is null then return; end if;

            update categorias set nombre = 'Canchas de Futbol', parent_id = null
            where nombre = 'Cancha de Futbol';
            update categorias set nombre = 'Canchas de Padle', parent_id = null
            where nombre = 'Cancha de Padel';
            update categorias set nombre = 'Tenis' where nombre = 'Cancha de Tenis';

            update categorias set parent_id = padre where nombre in ('Básquet', 'Vóley');
            insert into categorias (nombre, parent_id)
            select n, padre from unnest(array['Fútbol', 'Pádel']) n
            on conflict (nombre) do update set parent_id = excluded.parent_id;
        end
        $$;
        """
    )
