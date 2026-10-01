-- Un espacio deportivo no puede tener dos turnos superpuestos.
-- Espejo de ex_turno_no_solapa_por_empleado, aplicado solo a los turnos con cancha.
create extension if not exists "btree_gist" with schema "public";

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conname = 'ex_turno_no_solapa_por_cancha'
          and conrelid = 'public.turno'::regclass
    ) then
        alter table "public"."turno"
            add constraint "ex_turno_no_solapa_por_cancha"
            exclude using gist (
                id_cancha with =,
                tstzrange(fecha_hora_inicio, fecha_hora_fin, '[)'::text) with &&
            ) where (id_cancha is not null);
    end if;
end
$$;
