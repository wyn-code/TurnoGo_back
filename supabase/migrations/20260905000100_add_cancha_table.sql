-- Tabla cancha: espacios reservables de negocios de la categoría "Deportes".
create table if not exists "public"."cancha" (
    "id_cancha" integer not null,
    "nombre" character varying(100) not null,
    "activo" boolean not null default true,
    "id_negocio" integer not null,
    "created_at" timestamp without time zone default now() not null,
    "updated_at" timestamp without time zone default now() not null,
    constraint "cancha_pkey" primary key ("id_cancha")
);

create sequence if not exists "public"."cancha_id_cancha_seq"
    as integer start with 1 increment by 1 owned by "public"."cancha"."id_cancha";

alter table "public"."cancha"
    alter column "id_cancha" set default nextval('public.cancha_id_cancha_seq'::regclass);

alter table "public"."cancha"
    add constraint "cancha_id_negocio_fkey"
    foreign key ("id_negocio") references "public"."negocio" ("id_negocio")
    on delete cascade;

create index if not exists "ix_cancha_id_negocio"
    on "public"."cancha" using btree ("id_negocio");

create index if not exists "ix_cancha_id_cancha"
    on "public"."cancha" using btree ("id_cancha");
