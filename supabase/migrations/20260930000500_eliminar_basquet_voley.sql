-- Elimina las categorías Básquet y Vóley (sin uso). Espejo de alembic 20260930000500.
-- Aborta si algún negocio las usa, para no dejar negocios huérfanos.
do $$
begin
    if exists (
        select 1
        from negocio n
        join categorias c on c.id_categoria = n.id_categoria
        where c.nombre in ('Básquet', 'Basquet', 'Vóley', 'Voley')
    ) then
        raise exception 'Hay negocios en Básquet/Vóley: reasignarlos antes de eliminar las categorías';
    end if;

    delete from categorias where nombre in ('Básquet', 'Basquet', 'Vóley', 'Voley');
end
$$;
