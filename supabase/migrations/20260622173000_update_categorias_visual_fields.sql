alter table if exists "public"."categorias"
alter column "icono" type character varying(500);

alter table if exists "public"."categorias"
add column if not exists "descripcion" character varying(255);

insert into "public"."categorias" ("nombre", "icono", "descripcion")
values
    ('Peluquería', 'https://images.unsplash.com/photo-1560066984-138dadb4c035', 'Cortes, peinados, color y tratamientos capilares.'),
    ('Barbería', 'https://images.unsplash.com/photo-1503951914875-452162b0f3f1', 'Cortes masculinos, barba, perfilado y cuidado personal.'),
    ('Uñas', 'https://images.unsplash.com/photo-1604654894610-df63bc536371', 'Manicuria, esmaltado, nail art y servicios de cuidado de uñas.'),
    ('Estética', 'https://images.unsplash.com/photo-1519823551278-64ac92734fb1', 'Tratamientos faciales, corporales y servicios de belleza integral.'),
    ('Masajes', 'https://images.unsplash.com/photo-1544161515-4ab6ce6db874', 'Masajes relajantes, descontracturantes y terapias corporales.')
on conflict ("nombre") do update
set
    "icono" = excluded."icono",
    "descripcion" = excluded."descripcion";
