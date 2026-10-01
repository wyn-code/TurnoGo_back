-- cancha -> espacio (+ numero, descripcion). Espejo de alembic 20260930000200.
-- id_negocio NO es UNIQUE: un negocio multi-cancha tiene varios espacios.
do $$
begin
    if to_regclass('public.cancha') is not null then
        alter table "public"."cancha" rename to "espacio";
        alter table "public"."espacio" rename column "id_cancha" to "id_espacio";
        alter index if exists ix_cancha_id_cancha rename to ix_espacio_id_espacio;
        alter index if exists ix_cancha_id_negocio rename to idx_espacio_negocio;
        alter table "public"."espacio" rename constraint cancha_pkey to espacio_pkey;
        alter table "public"."espacio" rename constraint cancha_id_negocio_fkey to fk_espacio_negocio;
        alter sequence if exists cancha_id_cancha_seq rename to espacio_id_espacio_seq;
    end if;
end
$$;

alter table "public"."espacio" add column if not exists "numero" integer;
alter table "public"."espacio" add column if not exists "descripcion" text;

update "public"."espacio" e
set numero = r.n
from (
    select id_espacio,
           row_number() over (partition by id_negocio order by id_espacio) as n
    from "public"."espacio"
) r
where e.id_espacio = r.id_espacio and e.numero is null;

-- Un espacio por cada negocio Deportes (o sub-categoría) sin espacios.
insert into "public"."espacio" (nombre, numero, id_negocio, activo)
select left(n.nombre, 100), 1, n.id_negocio, true
from "public"."negocio" n
join "public"."categorias" c on c.id_categoria = n.id_categoria
where (c.nombre = 'Deportes'
       or c.parent_id in (select id_categoria from "public"."categorias" where nombre = 'Deportes'))
  and not exists (select 1 from "public"."espacio" e where e.id_negocio = n.id_negocio);
