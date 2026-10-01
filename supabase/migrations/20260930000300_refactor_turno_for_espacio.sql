-- turno: id_cancha -> id_espacio, empleado XOR espacio. Espejo de alembic 20260930000300.
create extension if not exists "btree_gist" with schema "public";

do $$
begin
    if exists (select 1 from information_schema.columns
               where table_schema = 'public' and table_name = 'turno' and column_name = 'id_cancha') then
        alter table "public"."turno" rename column "id_cancha" to "id_espacio";
        alter index if exists ix_turno_id_cancha rename to ix_turno_id_espacio;
        alter table "public"."turno" rename constraint turno_id_cancha_fkey to fk_turno_espacio;
        alter table "public"."turno" rename constraint ex_turno_no_solapa_por_cancha to ex_turno_no_solapa_espacio;
    end if;
end
$$;

-- Los turnos con ambos recursos (la app priorizaba el espacio) pierden el empleado.
update "public"."turno" set id_empleado = null
where id_empleado is not null and id_espacio is not null;

-- "Como máximo uno": existen turnos legítimos sin recurso (negocios sin empleados).
alter table "public"."turno" drop constraint if exists "chk_turno_no_empleado_y_espacio";
alter table "public"."turno"
    add constraint "chk_turno_no_empleado_y_espacio"
    check (id_empleado is null or id_espacio is null);

alter table "public"."turno" drop constraint if exists "ex_turno_no_solapa_por_empleado";
alter table "public"."turno" drop constraint if exists "ex_turno_no_solapa_empleado";
alter table "public"."turno"
    add constraint "ex_turno_no_solapa_empleado"
    exclude using gist (
        id_empleado with =,
        tstzrange(fecha_hora_inicio, fecha_hora_fin, '[)'::text) with &&
    ) where (id_empleado is not null);
