-- Categorías jerárquicas (espejo de alembic 20260930000100).
alter table "public"."categorias" add column if not exists "parent_id" integer;

do $$
begin
    if not exists (select 1 from pg_constraint where conname = 'categorias_parent_id_fkey') then
        alter table "public"."categorias"
            add constraint "categorias_parent_id_fkey"
            foreign key (parent_id) references public.categorias(id_categoria);
    end if;
end
$$;

create index if not exists "ix_categorias_parent_id" on "public"."categorias" (parent_id);

-- Deportes pasa a ser padre; los negocios existentes siguen apuntando a él.
insert into "public"."categorias" ("nombre", "parent_id")
select h.nombre, p.id_categoria
from (values ('Fútbol'), ('Pádel'), ('Tenis'), ('Básquet'), ('Vóley')) as h(nombre)
cross join (select id_categoria from "public"."categorias" where nombre = 'Deportes') p
on conflict (nombre) do update set parent_id = excluded.parent_id;
