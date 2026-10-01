"""Turno: empleado XOR espacio, multi-espacio y GET /turnos/disponibles.

El CHECK se ejercita contra SQLite; las exclusiones GiST (solapamiento) sólo
existen en Postgres y se prueban en test_migrations.py. Acá el solapamiento se
verifica a nivel aplicación (`hay_superposicion`).
"""

from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.estados_turno import CONFIRMADO, PENDIENTE
from app.models.categoria import Categoria
from app.models.cliente import Cliente
from app.models.empleado import Empleado
from app.models.espacio import Espacio
from app.models.negocio import Negocio
from app.models.servicio import Servicio
from app.models.turnos import Turno
from tests.auth_helpers import obtener_token

INICIO = datetime(2026, 10, 5, 10, 0)


@pytest.fixture(autouse=True)
def _cliente_en_db(db, seed_data):
    """Cliente 1 para los turnos insertados directo en la base."""
    db.add(Cliente(id_cliente=1, nombre="Base", apellido="Test", telefono="3364999000"))
    db.commit()


def _duenio(client):
    return obtener_token(client, "test1@test.com", "Test1234567!")


@pytest.fixture()
def cliente_id(client):
    res = client.post(
        "/api/clientes/get-or-create",
        json={"telefono": "3364000111", "nombre": "Ana", "apellido": "Test"},
    )
    return res.json()["id_cliente"]


def _espacio(client, nombre="Cancha 1"):
    res = client.post(
        "/api/espacios",
        json={"id_negocio": 1, "nombre": nombre},
        headers=obtener_token(client, "test1@test.com", "Test1234567!"),
    )
    return res.json()["id_espacio"]


def _post_turno(client, cliente_id, inicio=INICIO, **recurso):
    return client.post("/api/turnos/", json={
        "id_negocio": 1, "id_cliente": cliente_id, "id_servicio": 1,
        "fecha_hora_inicio": inicio.isoformat(), **recurso,
    })


# ── POST: empleado XOR espacio ──


def test_turno_con_espacio_sin_empleado_es_valido(client, seed_data, cliente_id):
    id_espacio = _espacio(client)
    res = _post_turno(client, cliente_id, id_espacio=id_espacio)
    assert res.status_code in (200, 201), res.text
    assert res.json()["id_espacio"] == id_espacio
    assert res.json()["id_cancha"] == id_espacio  # alias legado


def test_turno_con_empleado_y_espacio_es_rechazado(client, seed_data, cliente_id):
    id_espacio = _espacio(client)
    res = _post_turno(client, cliente_id, id_espacio=id_espacio, id_empleado=1)
    assert res.status_code == 400
    assert "no ambos" in res.json()["detail"]


def test_id_cancha_legado_se_acepta_como_espacio(client, seed_data, cliente_id):
    id_espacio = _espacio(client)
    res = _post_turno(client, cliente_id, id_cancha=id_espacio)
    assert res.status_code in (200, 201), res.text
    assert res.json()["id_espacio"] == id_espacio


def test_id_cancha_e_id_espacio_distintos_dan_422(client, seed_data, cliente_id):
    res = _post_turno(client, cliente_id, id_cancha=1, id_espacio=2)
    assert res.status_code == 422


def test_negocio_multi_espacio_exige_espacio(client, seed_data, cliente_id):
    _espacio(client)
    res = _post_turno(client, cliente_id, id_empleado=1)
    assert res.status_code == 400
    assert "id_espacio" in res.json()["detail"]

    assert _post_turno(client, cliente_id).status_code == 400  # sin recurso tampoco


def test_negocio_de_servicios_sigue_usando_empleado(client, seed_data, cliente_id):
    """Backward compatibility: sin espacios, el empleado funciona como siempre."""
    res = _post_turno(client, cliente_id, id_empleado=1)
    assert res.status_code in (200, 201), res.text
    assert res.json()["id_espacio"] is None
    assert res.json()["empleado"]["id_empleado"] == 1


def test_espacio_de_otro_negocio_es_rechazado(client, db, seed_data, cliente_id):
    db.add(Negocio(id_negocio=2, usuario_id=2, nombre="Otro", id_categoria=1,
                   wsp="1", direccion="x", ciudad="y", slug="otro", activo=True))
    db.flush()
    db.add(Espacio(id_espacio=50, id_negocio=2, nombre="Ajena"))
    db.commit()
    assert _post_turno(client, cliente_id, id_espacio=50).status_code == 400


# ── solapamiento por espacio ──


def test_solapamiento_por_espacio_da_409_y_otro_espacio_no(client, seed_data, cliente_id):
    e1, e2 = _espacio(client, "C1"), _espacio(client, "C2")
    assert _post_turno(client, cliente_id, id_espacio=e1).status_code in (200, 201)

    assert _post_turno(client, cliente_id, id_espacio=e1).status_code == 409
    assert _post_turno(client, cliente_id, id_espacio=e2).status_code in (200, 201)


def test_espacio_y_empleado_no_compiten_entre_si(client, db, seed_data, cliente_id):
    """Un turno de espacio no ocupa al empleado (y viceversa)."""
    from app.services.turno_service import hay_superposicion

    e1 = _espacio(client)
    _post_turno(client, cliente_id, id_espacio=e1)
    fin = datetime(2026, 10, 5, 10, 30)
    assert hay_superposicion(db, 1, 1, INICIO, fin, id_espacio=None) is False
    assert hay_superposicion(db, 1, None, INICIO, fin, id_espacio=e1) is True


# ── PUT: cambio de recurso ──


def test_cambiar_de_empleado_a_espacio_reemplaza_el_recurso(client, seed_data, cliente_id):
    id_turno = _post_turno(client, cliente_id, id_empleado=1).json()["id_turno"]
    id_espacio = _espacio(client)  # recién ahora el negocio pasa a multi-espacio

    res = client.put(
        f"/api/turnos/{id_turno}", json={"id_espacio": id_espacio}, headers=_duenio(client)
    )
    assert res.status_code == 200, res.text
    assert res.json()["id_espacio"] == id_espacio
    assert res.json()["empleado"] is None


def test_actualizar_con_ambos_recursos_da_400(client, seed_data, cliente_id):
    id_turno = _post_turno(client, cliente_id, id_empleado=1).json()["id_turno"]
    id_espacio = _espacio(client)
    res = client.put(
        f"/api/turnos/{id_turno}",
        json={"id_espacio": id_espacio, "id_empleado": 1},
        headers=_duenio(client),
    )
    assert res.status_code == 400


def test_editar_turno_previo_sin_tocar_recurso_no_se_invalida(client, seed_data, cliente_id):
    id_turno = _post_turno(client, cliente_id, id_empleado=1).json()["id_turno"]
    _espacio(client)  # el negocio pasa a multi-espacio después del turno
    res = client.put(
        f"/api/turnos/{id_turno}", json={"fecha_hora_inicio": "2026-10-05T15:00:00"}, headers=_duenio(client)
    )
    assert res.status_code == 200, res.text


# ── CHECK de DB y modelo ──


def test_check_de_db_rechaza_empleado_y_espacio(db, seed_data):
    db.add(Espacio(id_espacio=7, id_negocio=1, nombre="C"))
    db.commit()
    db.add(Turno(id_negocio=1, id_servicio=1, id_empleado=1, id_espacio=7, id_cliente=1,
                 id_estado=PENDIENTE, fecha_hora_inicio=INICIO, fecha_hora_fin=INICIO))
    with pytest.raises(IntegrityError, match="chk_turno_no_empleado_y_espacio"):
        db.flush()
    db.rollback()


def test_error_del_check_se_mapea_a_400():
    from fastapi import HTTPException
    from app.services.turno_service import _lanzar_error_integridad

    error = IntegrityError("stmt", {}, Exception(
        'new row violates check constraint "chk_turno_no_empleado_y_espacio"'))
    with pytest.raises(HTTPException) as exc:
        _lanzar_error_integridad(error)
    assert exc.value.status_code == 400


def test_error_de_exclusion_espacio_se_mapea_a_409():
    from fastapi import HTTPException
    from app.services.turno_service import _lanzar_error_integridad

    error = IntegrityError("stmt", {}, Exception('violates "ex_turno_no_solapa_espacio"'))
    with pytest.raises(HTTPException) as exc:
        _lanzar_error_integridad(error)
    assert exc.value.status_code == 409


def test_propiedad_recurso_devuelve_espacio_o_empleado(db, seed_data):
    db.add(Espacio(id_espacio=8, id_negocio=1, nombre="Cancha 8"))
    db.commit()
    base = dict(id_negocio=1, id_servicio=1, id_cliente=1, id_estado=PENDIENTE,
                fecha_hora_inicio=INICIO, fecha_hora_fin=INICIO)
    con_empleado = Turno(id_empleado=1, **base)
    con_espacio = Turno(id_espacio=8, **base)
    db.add_all([con_empleado, con_espacio])
    db.commit()

    assert con_empleado.recurso.nombre == "Juan"
    assert con_espacio.recurso.nombre == "Cancha 8"


# ── GET /turnos/disponibles ──


@pytest.fixture()
def escenario(db, seed_data, client):
    """Negocio 1 (Fútbol ⊂ Deportes, con espacio) y negocio 2 (Belleza, empleado)."""
    deportes = Categoria(nombre="Deportes")
    belleza = Categoria(nombre="Belleza")
    db.add_all([deportes, belleza])
    db.flush()
    futbol = Categoria(nombre="Fútbol", parent_id=deportes.id_categoria)
    db.add(futbol)
    db.flush()

    db.get(Negocio, 1).id_categoria = futbol.id_categoria
    db.add(Negocio(id_negocio=2, usuario_id=2, nombre="Peluquería", id_categoria=belleza.id_categoria,
                   wsp="1", direccion="x", ciudad="y", slug="pelu", activo=True))
    db.flush()
    db.add_all([
        Servicio(id_servicio=2, id_negocio=2, nombre_servicio="Corte", precio=1, duracion_min=30,
                 duracion_max=30, requiere_aprobacion=False, activo=True),
        Empleado(id_empleado=2, id_negocio=2, nombre="Lu", apellido="Gomez", telefono="1", activo=True),
        Espacio(id_espacio=20, id_negocio=1, nombre="Cancha 1"),
    ])
    db.flush()
    base = dict(id_cliente=1, fecha_hora_fin=INICIO)
    db.add_all([
        Turno(id_turno=1, id_negocio=1, id_servicio=1, id_espacio=20, id_estado=CONFIRMADO,
              fecha_hora_inicio=INICIO, **{**base, "fecha_hora_fin": INICIO}),
        Turno(id_turno=2, id_negocio=1, id_servicio=1, id_espacio=20, id_estado=PENDIENTE,
              fecha_hora_inicio=datetime(2026, 10, 6, 10, 0), **{**base, "fecha_hora_fin": INICIO}),
        Turno(id_turno=3, id_negocio=2, id_servicio=2, id_empleado=2, id_estado=CONFIRMADO,
              fecha_hora_inicio=INICIO, **{**base, "fecha_hora_fin": INICIO}),
    ])
    db.commit()
    return {"deportes": deportes.id_categoria, "futbol": futbol.id_categoria,
            "belleza": belleza.id_categoria}


def _ids(res):
    assert res.status_code == 200, res.text
    return sorted(t["id_turno"] for t in res.json())


def test_disponibles_filtra_por_categoria_padre_e_incluye_subcategorias(client, escenario):
    assert _ids(client.get(f"/api/turnos/disponibles?categoria_padre={escenario['deportes']}")) == [1, 2]
    assert _ids(client.get(f"/api/turnos/disponibles?categoria_padre={escenario['futbol']}")) == [1, 2]
    assert _ids(client.get(f"/api/turnos/disponibles?categoria_padre={escenario['belleza']}")) == [3]


def test_disponibles_filtra_por_fecha_y_estado(client, escenario):
    d = escenario["deportes"]
    assert _ids(client.get(f"/api/turnos/disponibles?categoria_padre={d}&fecha=2026-10-05")) == [1]
    assert _ids(client.get(f"/api/turnos/disponibles?categoria_padre={d}&estado={PENDIENTE}")) == [2]
    assert _ids(client.get("/api/turnos/disponibles?fecha=2026-10-05")) == [1, 3]


def test_disponibles_enriquece_con_espacio_o_empleado_sin_datos_del_cliente(client, escenario):
    filas = {t["id_turno"]: t for t in client.get("/api/turnos/disponibles").json()}
    assert filas[1]["recurso"] == {"tipo": "espacio", "id": 20, "nombre": "Cancha 1"}
    assert filas[3]["recurso"] == {"tipo": "empleado", "id": 2, "nombre": "Lu Gomez"}
    assert all("cliente" not in t for t in filas.values())


def test_get_turno_con_recurso(db, escenario):
    from app.services.turno_service import get_turno_con_recurso

    assert get_turno_con_recurso(db, 1)["recurso"]["tipo"] == "espacio"
    assert get_turno_con_recurso(db, 3)["recurso"]["tipo"] == "empleado"
    assert get_turno_con_recurso(db, 999) is None
