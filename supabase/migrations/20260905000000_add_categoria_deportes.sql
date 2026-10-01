-- Categoría "Deportes":canchas/padles/fields en lugar de empleados.
insert into "public"."categorias" ("nombre", "icono", "descripcion")
values
    ('Deportes', 'https://images.unsplash.com/photo-1574629810360-7efbbe195018', 'Canchas, canchetas, campos de fútbol y espacios deportivos para reservar por horario.')
on conflict ("nombre") do update
set
    "icono" = excluded."icono",
    "descripcion" = excluded."descripcion";
