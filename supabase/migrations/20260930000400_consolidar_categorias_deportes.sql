-- Consolida las categorías deportivas bajo "Deportes" (espejo de alembic 20260930000400).
-- Idempotente: se puede correr sobre una base con o sin las categorías sueltas previas.
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
