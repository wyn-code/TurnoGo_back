--turno.id_cancha: espacio deportivo reservado (negocios de la categoría "Deportes").
-- Nullable a propósito: los negocios de servicios siguen reservando por empleado.
alter table "public"."turno"
    add column if not exists "id_cancha" integer;

alter table "public"."turno"
    add constraint "turno_id_cancha_fkey"
    foreign key ("id_cancha") references "public"."cancha" ("id_cancha")
    on delete set null;

create index if not exists "ix_turno_id_cancha"
    on "public"."turno" using btree ("id_cancha");

-- Backfill explícito: los turnos preexistentes no pertenecen a ningún espacio.
update "public"."turno" set "id_cancha" = null where "id_cancha" is not null;
