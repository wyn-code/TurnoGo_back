"""Tests de las migraciones 20260930* (categorías jerárquicas, espacio, turno).

Necesitan PostgreSQL real (EXCLUDE USING GIST no existe en SQLite). Se activan
con la variable de entorno TEST_POSTGRES_URL, p. ej.:

    TEST_POSTGRES_URL=postgresql+psycopg2://postgres@127.0.0.1:5432/turnogo_test

La base se vacía en cada test: usar una base descartable.

Cada test arma el esquema previo (tabla `cancha` incluida, ejecutando las
migraciones reales 20260905*), siembra datos y corre upgrade/downgrade.
"""

import importlib.util
import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

pytest.importorskip("alembic")
from alembic.operations import Operations  # noqa: E402
from alembic.runtime.migration import MigrationContext  # noqa: E402

URL = os.environ.get("TEST_POSTGRES_URL")
pytestmark = pytest.mark.skipif(not URL, reason="TEST_POSTGRES_URL no definida")

VERSIONS = Path(__file__).resolve().parent.parent / "alembic" / "versions"
PREVIAS = ["20260905000100_add_cancha_table", "20260905000200_add_turno_id_cancha",
           "20260905000300_add_turno_exclude_cancha"]
NUEVAS = ["20260930000100_add_parent_id_categorias", "20260930000200_espacio_table",
          "20260930000300_refactor_turno_for_espacio",
          "20260930000400_consolidar_categorias_deportes",
          "20260930000500_eliminar_basquet_voley"]

ESQUEMA_PREVIO = """
drop schema public cascade; create schema public;
create extension btree_gist;
create table categorias (
    id_categoria serial primary key, nombre varchar(100) not null unique,
    icono varchar(500), descripcion varchar(255), created_at timestamp default now());
create table negocio (
    id_negocio serial primary key, nombre varchar(100) not null,
    id_categoria integer references categorias(id_categoria));
create table empleado (id_empleado serial primary key, id_negocio integer references negocio);
create table turno (
    id_turno serial primary key, id_negocio integer not null references negocio,
    id_empleado integer references empleado(id_empleado),
    fecha_hora_inicio timestamptz not null, fecha_hora_fin timestamptz,
    constraint ex_turno_no_solapa_por_empleado exclude using gist (
        id_empleado with =, tstzrange(fecha_hora_inicio, fecha_hora_fin, '[)'::text) with &&));
"""

SEMILLA = """
insert into categorias (id_categoria, nombre) values
    (1, 'Deportes'), (2, 'Belleza'), (3, 'Canchas de Futbol'), (4, 'Canchas de Padle');
insert into negocio (id_negocio, nombre, id_categoria) values
    (1, 'Cancha Norte', 1), (2, 'Club Sur', 1), (3, 'Peluquería', 2),
    (4, 'Camp Nou', 3), (5, 'El Galpon', 4);
insert into empleado (id_empleado, id_negocio) values (1, 3), (2, 2);
insert into cancha (id_cancha, nombre, id_negocio) values (10, 'C1', 2), (11, 'C2', 2);
insert into turno (id_turno, id_negocio, id_empleado, id_cancha, fecha_hora_inicio, fecha_hora_fin) values
    (1, 3, 1,    null, '2026-10-01 10:00', '2026-10-01 11:00'),  -- servicios: empleado
    (2, 2, null, 10,   '2026-10-01 10:00', '2026-10-01 11:00'),  -- cancha
    (3, 2, 2,    11,   '2026-10-01 10:00', '2026-10-01 11:00'),  -- ambos (legado)
    (4, 3, null, null, '2026-10-01 12:00', '2026-10-01 13:00');  -- sin recurso
select setval('categorias_id_categoria_seq', 100), setval('cancha_id_cancha_seq', 100);
"""


def _correr(conn, nombre, accion):
    spec = importlib.util.spec_from_file_location(nombre, VERSIONS / f"{nombre}.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    with Operations.context(MigrationContext.configure(conn)):
        getattr(modulo, accion)()


@pytest.fixture()
def conn():
    engine = create_engine(URL, isolation_level="AUTOCOMMIT")
    with engine.connect() as c:
        for sentencia in ESQUEMA_PREVIO.split(";\n"):
            if sentencia.strip():
                c.execute(text(sentencia))
        for nombre in PREVIAS:
            _correr(c, nombre, "upgrade")
        c.execute(text(SEMILLA))
        yield c
    engine.dispose()


@pytest.fixture()
def migrada(conn):
    for nombre in NUEVAS:
        _correr(conn, nombre, "upgrade")
    return conn


def _scalar(conn, sql, **params):
    return conn.execute(text(sql), params).scalar()


def _columnas(conn, tabla):
    filas = conn.execute(text(
        "select column_name from information_schema.columns "
        "where table_schema='public' and table_name=:t"), {"t": tabla})
    return {f[0] for f in filas}


def _insertar_turno(conn, id_turno, empleado, espacio, inicio, fin):
    conn.execute(text(
        "insert into turno (id_turno, id_negocio, id_empleado, id_espacio, "
        "fecha_hora_inicio, fecha_hora_fin) values (:i, 2, :e, :s, :a, :b)"),
        {"i": id_turno, "e": empleado, "s": espacio, "a": inicio, "b": fin})


# ── categorias.parent_id ──


def test_parent_id_agregado_con_indice_y_jerarquia_deportes(migrada):
    assert "parent_id" in _columnas(migrada, "categorias")
    assert _scalar(migrada, "select 1 from pg_indexes where indexname='ix_categorias_parent_id'") == 1

    hijos = {f[0] for f in migrada.execute(text(
        "select nombre from categorias where parent_id = "
        "(select id_categoria from categorias where nombre='Deportes')"))}
    assert hijos == {"Cancha de Futbol", "Cancha de Padel", "Cancha de Tenis"}
    # Las categorías sin jerarquía siguen siendo raíces y los negocios no se movieron.
    assert _scalar(migrada, "select parent_id from categorias where nombre='Belleza'") is None
    assert _scalar(migrada, "select id_categoria from negocio where id_negocio=1") == 1


# ── consolidación de categorías deportivas (20260930000400) ──


def _cat(conn, nombre):
    return conn.execute(text("select id_categoria, parent_id from categorias where nombre=:n"),
                        {"n": nombre}).first()


def test_consolida_categorias_sueltas_bajo_deportes(migrada):
    deportes = _cat(migrada, "Deportes")[0]
    # Las raíces sueltas con negocios se conservan, renombradas y reubicadas.
    assert _cat(migrada, "Cancha de Futbol")[1] == deportes
    assert _cat(migrada, "Cancha de Padel")[1] == deportes
    assert _cat(migrada, "Cancha de Tenis")[1] == deportes
    # Los nombres viejos y las hijas duplicadas ya no existen.
    for viejo in ("Canchas de Futbol", "Canchas de Padle", "Fútbol", "Pádel", "Tenis"):
        assert _cat(migrada, viejo) is None


def test_negocios_conservan_su_categoria_tras_consolidar(migrada):
    nombre = lambda id_negocio: _scalar(
        migrada,
        "select c.nombre from negocio n join categorias c using (id_categoria) "
        "where n.id_negocio=:i", i=id_negocio)
    assert nombre(4) == "Cancha de Futbol"   # Camp Nou
    assert nombre(5) == "Cancha de Padel"    # El Galpon
    assert nombre(3) == "Belleza"
    # Ningún negocio apunta a una categoría inexistente.
    assert _scalar(migrada, "select count(*) from negocio n left join categorias c "
                            "using (id_categoria) where n.id_categoria is not null "
                            "and c.id_categoria is null") == 0


def test_negocios_movidos_a_deportes_reciben_un_espacio(migrada):
    assert _scalar(migrada, "select nombre from espacio where id_negocio=4") == "Camp Nou"
    assert _scalar(migrada, "select nombre from espacio where id_negocio=5") == "El Galpon"


def test_consolidacion_es_idempotente(migrada):
    antes = _scalar(migrada, "select count(*) from categorias")
    _correr(migrada, "20260930000400_consolidar_categorias_deportes", "upgrade")
    assert _scalar(migrada, "select count(*) from categorias") == antes
    assert _scalar(migrada, "select count(*) from espacio where id_negocio=4") == 1


# ── eliminación de Básquet / Vóley (20260930000500) ──


def test_basquet_y_voley_se_eliminan_sin_romper_fks(migrada):
    for nombre in ("Básquet", "Vóley"):
        assert _cat(migrada, nombre) is None
    assert _scalar(migrada, "select count(*) from negocio n left join categorias c "
                            "using (id_categoria) where n.id_categoria is not null "
                            "and c.id_categoria is null") == 0
    # El resto del árbol sigue intacto.
    assert _cat(migrada, "Cancha de Padel") is not None


def test_no_elimina_si_algun_negocio_usa_la_categoria(conn):
    for nombre in NUEVAS[:-1]:
        _correr(conn, nombre, "upgrade")
    conn.execute(text("insert into negocio (id_negocio, nombre, id_categoria) "
                      "values (90, 'Club Vóley', (select id_categoria from categorias where nombre='Vóley'))"))
    with pytest.raises(Exception, match="reasignarlos"):
        _correr(conn, NUEVAS[-1], "upgrade")
    assert _cat(conn, "Vóley") is not None


# ── espacio ──


def test_cancha_se_renombra_a_espacio_con_columnas_nuevas(migrada):
    assert _scalar(migrada, "select to_regclass('public.cancha')") is None
    cols = _columnas(migrada, "espacio")
    assert {"id_espacio", "numero", "descripcion", "id_negocio"} <= cols
    assert "id_cancha" not in cols
    assert _scalar(migrada, "select 1 from pg_indexes where indexname='idx_espacio_negocio'") == 1


def test_espacio_por_cada_negocio_deportes_sin_espacios(migrada):
    # Cancha Norte no tenía canchas: recibe un espacio con su nombre.
    assert _scalar(migrada, "select nombre from espacio where id_negocio=1") == "Cancha Norte"
    # Club Sur conserva las suyas, ahora numeradas; la peluquería no recibe ninguno.
    numeros = [f[0] for f in migrada.execute(text(
        "select numero from espacio where id_negocio=2 order by id_espacio"))]
    assert numeros == [1, 2]
    assert _scalar(migrada, "select count(*) from espacio where id_negocio=3") == 0


def test_negocio_puede_tener_varios_espacios(migrada):
    migrada.execute(text("insert into espacio (nombre, id_negocio) values ('Otra', 1)"))
    assert _scalar(migrada, "select count(*) from espacio where id_negocio=1") == 2


def test_espacio_se_borra_en_cascada_con_el_negocio(migrada):
    migrada.execute(text("delete from turno where id_negocio=2"))
    migrada.execute(text("delete from empleado where id_negocio=2"))
    migrada.execute(text("delete from negocio where id_negocio=2"))
    assert _scalar(migrada, "select count(*) from espacio where id_negocio=2") == 0


# ── turno ──


def test_turnos_existentes_se_migran_sin_violar_el_check(migrada):
    filas = {f[0]: (f[1], f[2]) for f in migrada.execute(text(
        "select id_turno, id_empleado, id_espacio from turno"))}
    assert filas[1] == (1, None)        # servicios: conserva empleado, sin espacio
    assert filas[2] == (None, 10)       # cancha -> espacio
    assert filas[3] == (None, 11)       # ambos: gana el espacio
    assert filas[4] == (None, None)     # sin recurso: se respeta
    assert "id_cancha" not in _columnas(migrada, "turno")


def test_check_rechaza_empleado_y_espacio(migrada):
    with pytest.raises(IntegrityError, match="chk_turno_no_empleado_y_espacio"):
        _insertar_turno(migrada, 50, 2, 10, "2026-11-01 10:00", "2026-11-01 11:00")


def test_solapamiento_por_empleado_sigue_bloqueado(migrada):
    with pytest.raises(IntegrityError, match="ex_turno_no_solapa_empleado"):
        _insertar_turno(migrada, 51, 1, None, "2026-10-01 10:30", "2026-10-01 11:30")


def test_solapamiento_por_espacio_bloqueado_pero_no_entre_espacios(migrada):
    with pytest.raises(IntegrityError, match="ex_turno_no_solapa_espacio"):
        _insertar_turno(migrada, 52, None, 10, "2026-10-01 10:30", "2026-10-01 11:30")
    # Otro espacio, o el mismo espacio pegado al turno previo ('[)'), no solapa.
    otro = _scalar(migrada, "select id_espacio from espacio where id_negocio=1")
    _insertar_turno(migrada, 53, None, otro, "2026-10-01 10:30", "2026-10-01 11:30")
    _insertar_turno(migrada, 54, None, 10, "2026-10-01 11:00", "2026-10-01 12:00")


def test_turnos_sin_recurso_no_se_excluyen_entre_si(migrada):
    _insertar_turno(migrada, 55, None, None, "2026-10-01 12:00", "2026-10-01 13:00")


# ── reversibilidad ──


def test_downgrade_restaura_el_esquema_previo_y_se_puede_reaplicar(migrada):
    for nombre in reversed(NUEVAS):
        _correr(migrada, nombre, "downgrade")

    assert _scalar(migrada, "select to_regclass('public.espacio')") is None
    assert "id_cancha" in _columnas(migrada, "turno")
    assert "parent_id" not in _columnas(migrada, "categorias")
    assert _scalar(migrada, "select 1 from pg_constraint where conname='ex_turno_no_solapa_por_empleado'") == 1
    assert _scalar(migrada, "select 1 from pg_constraint where conname='ex_turno_no_solapa_por_cancha'") == 1
    assert _scalar(migrada, "select count(*) from categorias where nombre='Fútbol'") == 0

    for nombre in NUEVAS:
        _correr(migrada, nombre, "upgrade")
    assert "id_espacio" in _columnas(migrada, "turno")
