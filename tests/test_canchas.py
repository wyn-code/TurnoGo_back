from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from tests.auth_helpers import obtener_token


RUTA_CANCHAS = "/api/canchas"
RUTA_TURNOS = "/api/turnos"
RUTA_NEGOCIOS = "/api/negocios"


def _headers_duenio(client):
    return obtener_token(client, "test1@test.com", "Test1234567!")


def _headers_ajeno(client):
    return obtener_token(client, "test2@test.com", "Test1234567!")


def _sin_geocoding(monkeypatch):
    """El onboarding llama a Mapbox; en tests no hay red."""
    import app.services.negocio_service as negocio_service

    monkeypatch.setattr(
        negocio_service,
        "obtener_coordenadas",
        lambda **kwargs: None,
    )


def _crear_categoria_deportes(db) -> int:
    from app.models.categoria import Categoria

    categoria = (
        db.query(Categoria)
        .filter(Categoria.nombre == "Deportes")
        .first()
    )

    if categoria is None:
        categoria = Categoria(nombre="Deportes")
        db.add(categoria)
        db.commit()
        db.refresh(categoria)

    return categoria.id_categoria


def _crear_cliente(client: TestClient, telefono: str, nombre="Bruno") -> int:
    res = client.post(
        "/api/clientes/get-or-create",
        json={"telefono": telefono, "nombre": nombre, "apellido": "Test"},
    )
    assert res.status_code == 200, res.text
    return res.json()["id_cliente"]


def _crear_negocio_deportes(
    client: TestClient,
    nombre: str,
    cantidad_espacios: int | None,
    id_categoria: int,
    extra: dict | None = None,
):
    payload = {
        "nombre": nombre,
        "wsp": "3364555000",
        "direccion": "Mitre 123",
        "ciudad": "San Nicolas",
        "activo": True,
        "id_categoria": id_categoria,
        **(extra or {}),
    }

    if cantidad_espacios is not None:
        payload["cantidad_espacios"] = cantidad_espacios

    return client.post(
        RUTA_NEGOCIOS,
        json=payload,
        headers=_headers_ajeno(client),
    )


def _crear_cancha(client: TestClient, id_negocio: int, nombre: str, headers=None):
    return client.post(
        f"{RUTA_CANCHAS}/negocio/{id_negocio}",
        json={"nombre": nombre},
        headers=headers if headers is not None else _headers_duenio(client),
    )


def _crear_turno(
    client: TestClient,
    seed_data,
    id_cliente: int,
    inicio: datetime,
    id_cancha=None,
    id_empleado="empleado",
):
    payload = {
        "id_negocio": seed_data["negocio"].id_negocio,
        "id_cliente": id_cliente,
        "id_servicio": seed_data["servicio"].id_servicio,
        "fecha_hora_inicio": inicio.isoformat(),
    }

    if id_empleado == "empleado":
        payload["id_empleado"] = seed_data["empleado"].id_empleado
    elif id_empleado is not None:
        payload["id_empleado"] = id_empleado

    if id_cancha is not None:
        payload["id_cancha"] = id_cancha

    return client.post(RUTA_TURNOS, json=payload)


# ── ONBOARDING: canchas creadas automáticamente ──


def test_crear_cancha_deportes(client: TestClient, db, seed_data, monkeypatch):
    _sin_geocoding(monkeypatch)
    id_categoria = _crear_categoria_deportes(db)

    response = _crear_negocio_deportes(
        client, "Club Padle Norte", 2, id_categoria
    )
    assert response.status_code in (200, 201), response.text

    body = response.json()
    canchas = body["canchas"]

    assert len(canchas) == 2
    assert [c["nombre"] for c in canchas] == ["Cancha 1", "Cancha 2"]
    assert all(c["activo"] is True for c in canchas)
    assert all(c["id_negocio"] == body["id_negocio"] for c in canchas)
    assert id_categoria == body["id_categoria"]


def test_crear_negocio_deportes_acepta_lista_de_canchas(
    client: TestClient,
    db,
    seed_data,
    monkeypatch,
):
    _sin_geocoding(monkeypatch)
    id_categoria = _crear_categoria_deportes(db)

    response = _crear_negocio_deportes(
        client,
        "Complejo Futbol",
        None,
        id_categoria,
        extra={
            "canchas": [
                {"nombre": "Cancha A"},
                {"nombre": "Cancheta 1"},
                {"nombre": "  "},
            ],
        },
    )
    assert response.status_code in (200, 201), response.text

    canchas = response.json()["canchas"]
    # Los nombres en blanco se descartan.
    assert [c["nombre"] for c in canchas] == ["Cancha A", "Cancheta 1"]


def test_crear_negocio_sin_deportes_no_crea_canchas(
    client: TestClient,
    db,
    seed_data,
    monkeypatch,
):
    _sin_geocoding(monkeypatch)

    response = _crear_negocio_deportes(
        client,
        "Peluqueria Rosa",
        3,
        1,
        extra={
            "empleados": [
                {"nombre": "Juan", "apellido": "Perez", "telefono": "3364001111"}
            ],
        },
    )
    assert response.status_code in (200, 201), response.text

    body = response.json()
    assert body["canchas"] == []
    assert len(body["empleados"]) == 1


# ── ROUTER /canchas ──


def test_listar_canchas_es_publico(client: TestClient, seed_data):
    canchas = client.get(f"{RUTA_CANCHAS}/negocio/{seed_data['negocio'].id_negocio}")
    assert canchas.status_code == 200
    assert canchas.json() == []


def test_crear_cancha_exige_autenticacion(client: TestClient, seed_data):
    response = client.post(
        f"{RUTA_CANCHAS}/negocio/{seed_data['negocio'].id_negocio}",
        json={"nombre": "Cancha 1"},
    )
    assert response.status_code == 401


def test_listar_canchas_oculta_inactivas_salvo_que_se_pidan(client: TestClient, seed_data):
    id_negocio = seed_data["negocio"].id_negocio
    activa = _crear_cancha(client, id_negocio, "Cancha 1").json()

    borrada = _crear_cancha(client, id_negocio, "Cancha 2")
    borrada = client.delete(
        f"{RUTA_CANCHAS}/{borrada.json()['id_cancha']}",
        headers=_headers_duenio(client),
    )
    assert borrada.status_code == 200

    publicas = client.get(f"{RUTA_CANCHAS}/negocio/{id_negocio}")
    assert publicas.status_code == 200
    assert [c["nombre"] for c in publicas.json()] == ["Cancha 1"]

    todas = client.get(
        f"{RUTA_CANCHAS}/negocio/{id_negocio}",
        params={"incluir_inactivas": True},
    )
    assert todas.status_code == 200
    assert {c["id_cancha"] for c in todas.json()} == {
        activa["id_cancha"],
        activa["id_cancha"] + 1,
    }


def test_crear_cancha_de_negocio_ajeno_da_403(client: TestClient, seed_data):
    response = _crear_cancha(
        client,
        seed_data["negocio"].id_negocio,
        "Cancha 1",
        headers=_headers_ajeno(client),
    )
    assert response.status_code == 403
    assert "permisos" in response.json()["detail"].lower()


def test_crear_cancha_en_negocio_inexistente_da_404(client: TestClient, seed_data):
    response = client.post(
        f"{RUTA_CANCHAS}/negocio/9999",
        json={"nombre": "Cancha 1"},
        headers=_headers_duenio(client),
    )
    assert response.status_code == 404


def test_crear_listar_actualizar_y_borrar_cancha(client: TestClient, seed_data):
    id_negocio = seed_data["negocio"].id_negocio

    creada = _crear_cancha(client, id_negocio, "  Cancha 1  ")
    assert creada.status_code == 201, creada.text
    id_cancha = creada.json()["id_cancha"]
    assert creada.json()["nombre"] == "Cancha 1"
    assert creada.json()["activo"] is True

    listado = client.get(f"{RUTA_CANCHAS}/negocio/{id_negocio}")
    assert listado.status_code == 200
    assert [c["id_cancha"] for c in listado.json()] == [id_cancha]

    actualizada = client.put(
        f"{RUTA_CANCHAS}/{id_cancha}",
        json={"nombre": "Cancha-central"},
        headers=_headers_duenio(client),
    )
    assert actualizada.status_code == 200
    assert actualizada.json()["nombre"] == "Cancha-central"

    borrada = client.delete(
        f"{RUTA_CANCHAS}/{id_cancha}",
        headers=_headers_duenio(client),
    )
    assert borrada.status_code == 200

    # Baja lógica: desaparece del listado público.
    listado = client.get(f"{RUTA_CANCHAS}/negocio/{id_negocio}")
    assert listado.json() == []


def test_borrar_cancha_de_negocio_ajeno_da_403(client: TestClient, seed_data):
    creada = _crear_cancha(client, seed_data["negocio"].id_negocio, "Cancha 1")
    id_cancha = creada.json()["id_cancha"]

    response = client.delete(
        f"{RUTA_CANCHAS}/{id_cancha}",
        headers=_headers_ajeno(client),
    )
    assert response.status_code == 403


# ── SUPERPOSICIÓN POR CANCHA ──


def test_superposicion_canchas(client: TestClient, seed_data):
    id_cliente = _crear_cliente(client, "3364777001")
    cancha_1 = _crear_cancha(client, seed_data["negocio"].id_negocio, "Cancha 1").json()
    cancha_2 = _crear_cancha(client, seed_data["negocio"].id_negocio, "Cancha 2").json()

    inicio = datetime(2026, 4, 20, 10, 0, 0)

    primero = _crear_turno(
        client, seed_data, id_cliente, inicio,
        id_cancha=cancha_1["id_cancha"], id_empleado=None,
    )
    assert primero.status_code == 201, primero.text
    assert primero.json()["id_cancha"] == cancha_1["id_cancha"]

    # Misma cancha, horario solapado -> 409.
    segundo = _crear_turno(
        client, seed_data, id_cliente, inicio + timedelta(minutes=15),
        id_cancha=cancha_1["id_cancha"], id_empleado=None,
    )
    assert segundo.status_code == 409, segundo.text
    assert "cancha" in segundo.json()["detail"].lower()

    # Misma cancha, horario contiguo (fin == inicio) -> OK.
    contiguo = _crear_turno(
        client, seed_data, id_cliente, inicio + timedelta(minutes=30),
        id_cancha=cancha_1["id_cancha"], id_empleado=None,
    )
    assert contiguo.status_code == 201, contiguo.text

    # Cancha distinta, mismo horario -> OK.
    otra = _crear_turno(
        client, seed_data, id_cliente, inicio,
        id_cancha=cancha_2["id_cancha"], id_empleado=None,
    )
    assert otra.status_code == 201, otra.text


def test_turnos_canchas_distintas(client: TestClient, seed_data):
    id_cliente = _crear_cliente(client, "3364777002")
    cancha_1 = _crear_cancha(client, seed_data["negocio"].id_negocio, "Cancha 1").json()
    cancha_2 = _crear_cancha(client, seed_data["negocio"].id_negocio, "Cancha 2").json()

    inicio = datetime(2026, 4, 21, 18, 0, 0)

    for cancha in (cancha_1, cancha_2):
        response = _crear_turno(
            client, seed_data, id_cliente, inicio,
            id_cancha=cancha["id_cancha"], id_empleado=None,
        )
        assert response.status_code == 201, response.text


def test_prioridad_cancha_sobre_empleado(client: TestClient, db, seed_data):
    """Con id_cancha cargada manda la cancha, no el empleado."""
    from app.services.turno_service import hay_superposicion

    id_cliente = _crear_cliente(client, "3364777003")
    cancha_1 = _crear_cancha(client, seed_data["negocio"].id_negocio, "Cancha 1").json()
    cancha_2 = _crear_cancha(client, seed_data["negocio"].id_negocio, "Cancha 2").json()

    inicio = datetime(2026, 4, 22, 9, 0, 0)
    fin = inicio + timedelta(minutes=30)

    _crear_turno(
        client, seed_data, id_cliente, inicio,
        id_cancha=cancha_1["id_cancha"], id_empleado=None,
    )

    id_negocio = seed_data["negocio"].id_negocio
    id_empleado = seed_data["empleado"].id_empleado

    # Otra cancha -> libre, aunque comparta empleado con el turno anterior.
    assert hay_superposicion(
        db,
        id_negocio=id_negocio,
        id_empleado=id_empleado,
        inicio=inicio,
        fin=fin,
        id_espacio=cancha_2["id_cancha"],
    ) is False

    # La misma cancha -> ocupada.
    assert hay_superposicion(
        db,
        id_negocio=id_negocio,
        id_empleado=None,
        inicio=inicio,
        fin=fin,
        id_espacio=cancha_1["id_cancha"],
    ) is True


def test_turno_con_cancha_de_otro_negocio_da_400(client: TestClient, db, seed_data):
    from app.models.cancha import Cancha
    from app.models.negocio import Negocio

    cancha_ajena = _crear_cancha(
        client, seed_data["negocio"].id_negocio, "Cancha ajena"
    ).json()

    # Reasignamos la cancha a otro negocio (usuario 2) directamente en la DB.
    negocio_ajeno = Negocio(
        usuario_id=2,
        nombre="Negocio Ajeno",
        wsp="3364666000",
        direccion="Belgrano 456",
        ciudad="San Nicolas",
        slug="negocio-ajeno",
        activo=True,
        id_categoria=1,
    )
    db.add(negocio_ajeno)
    db.commit()

    db_cancha = (
        db.query(Cancha)
        .filter(Cancha.id_cancha == cancha_ajena["id_cancha"])
        .first()
    )
    db_cancha.id_negocio = negocio_ajeno.id_negocio
    db.commit()

    id_cliente = _crear_cliente(client, "3364777004")
    response = _crear_turno(
        client, seed_data, id_cliente, datetime(2026, 4, 23, 11, 0, 0),
        id_cancha=cancha_ajena["id_cancha"], id_empleado=None,
    )
    assert response.status_code == 400
    assert "cancha" in response.json()["detail"].lower()


def test_turno_con_cancha_inactiva_da_400(client: TestClient, seed_data):
    cancha = _crear_cancha(client, seed_data["negocio"].id_negocio, "Cancha 1").json()
    client.put(
        f"{RUTA_CANCHAS}/{cancha['id_cancha']}",
        json={"activo": False},
        headers=_headers_duenio(client),
    )

    id_cliente = _crear_cliente(client, "3364777005")
    response = _crear_turno(
        client, seed_data, id_cliente, datetime(2026, 4, 24, 11, 0, 0),
        id_cancha=cancha["id_cancha"], id_empleado=None,
    )
    assert response.status_code == 400


def test_no_solapa_cancha_excluyendo_el_mismo_turno(client: TestClient, seed_data):
    id_cliente = _crear_cliente(client, "3364777006")
    cancha = _crear_cancha(client, seed_data["negocio"].id_negocio, "Cancha 1").json()
    inicio = datetime(2026, 4, 25, 15, 0, 0)

    creado = _crear_turno(
        client, seed_data, id_cliente, inicio,
        id_cancha=cancha["id_cancha"], id_empleado=None,
    )
    assert creado.status_code == 201, creado.text

    actualizado = client.put(
        f"{RUTA_TURNOS}/{creado.json()['id_turno']}",
        json={"id_cancha": cancha["id_cancha"]},
        headers=_headers_duenio(client),
    )
    assert actualizado.status_code == 200, actualizado.text
    assert actualizado.json()["id_cancha"] == cancha["id_cancha"]


# ── DISPONIBILIDAD ──


def test_disponibilidad_filtra_por_cancha(client: TestClient, seed_data):
    id_cliente = _crear_cliente(client, "3364777007")
    cancha_1 = _crear_cancha(client, seed_data["negocio"].id_negocio, "Cancha 1").json()
    cancha_2 = _crear_cancha(client, seed_data["negocio"].id_negocio, "Cancha 2").json()

    inicio = datetime(2026, 4, 26, 16, 0, 0)
    _crear_turno(
        client, seed_data, id_cliente, inicio,
        id_cancha=cancha_1["id_cancha"], id_empleado=None,
    )

    params = {
        "id_negocio": seed_data["negocio"].id_negocio,
        "desde": inicio.isoformat(),
        "hasta": (inicio + timedelta(hours=2)).isoformat(),
    }

    solo_cancha_1 = client.get(f"{RUTA_TURNOS}/disponibilidad", params={
        **params, "id_cancha": cancha_1["id_cancha"],
    })
    assert solo_cancha_1.status_code == 200
    assert [t["id_cancha"] for t in solo_cancha_1.json()] == [cancha_1["id_cancha"]]

    solo_cancha_2 = client.get(f"{RUTA_TURNOS}/disponibilidad", params={
        **params, "id_cancha": cancha_2["id_cancha"],
    })
    assert solo_cancha_2.status_code == 200
    assert solo_cancha_2.json() == []

    # id_cancha tiene prioridad sobre id_empleado.
    con_ambos = client.get(f"{RUTA_TURNOS}/disponibilidad", params={
        **params,
        "id_cancha": cancha_2["id_cancha"],
        "id_empleado": seed_data["empleado"].id_empleado,
    })
    assert con_ambos.status_code == 200
    assert con_ambos.json() == []


# ── CONSTRAINT DE BASE DE DATOS ──
#
# SQLite (base de los tests) no soporta EXCLUDE USING GIST, así que el
# constraint ex_turno_no_solapa_por_cancha no se puede exercising acá. Se
# verifica el mapeo del IntegrityError de Postgres al 409 del servicio.


def test_error_integridad_cancha_devuelve_409():
    from app.services.turno_service import _lanzar_error_integridad

    error = IntegrityError("stmt", {}, Exception(
        'duplicate key value violates unique constraint '
        '"ex_turno_no_solapa_por_cancha"'
    ))

    with pytest.raises(HTTPException) as exc_info:
        _lanzar_error_integridad(error)

    assert exc_info.value.status_code == 409
    assert "cancha" in exc_info.value.detail.lower()


def test_negocio_deportes_no_crea_empleados(client: TestClient, db, seed_data, monkeypatch):
    _sin_geocoding(monkeypatch)
    id_categoria = _crear_categoria_deportes(db)

    response = _crear_negocio_deportes(client, "Club Natacion", 1, id_categoria)
    assert response.status_code in (200, 201), response.text
    assert response.json()["empleados"] == []
    assert len(response.json()["canchas"]) == 1
