from datetime import datetime

import pytest

from app.models.cliente import Cliente
from app.models.empleado import Empleado
from app.models.estado_turno import EstadoTurno
from app.models.negocio import Negocio
from app.models.servicio import Servicio
from app.models.turnos import Turno


@pytest.fixture
def datos_base(db):

    negocio = Negocio(
        id_negocio=1,
        nombre="Negocio Test",
        rubro="Barberia",
        wsp="123456789",
        telefono="3364000000",
        direccion="Calle Falsa 123",
        ciudad="San Nicolas",
        slug="negocio-test",   # 🔥 ESTO ES LO QUE FALTA
        activo=True,           # 🔥 recomendable
    )

    cliente_1 = Cliente(
        id_cliente=1,
        nombre_clt="Juan",
        apellido_clt="Perez",
        telefono_clt="111111111",
    )

    cliente_2 = Cliente(
        id_cliente=2,
        nombre_clt="Ana",
        apellido_clt="Gomez",
        telefono_clt="222222222",
    )

    servicio_1 = Servicio(
        id_servicio=1,
        nombre_servicio="Corte",
        precio=1000,
        requiere_aprobacion=False,
        duracion_min=30,
        duracion_max=30,
        activo=True,
    )

    servicio_2 = Servicio(
        id_servicio=2,
        nombre_servicio="Color",
        precio=3000,
        requiere_aprobacion=True,
        duracion_min=90,
        duracion_max=90,
        activo=True,
    )

    estado = EstadoTurno(
        id_estado=1,
        nombre_estado="Pendiente",
    )

    empleado_1 = Empleado(
        id_empleado=1,
        nombre="Pedro",
        apellido="Lopez",
        telefono="333333333",
        activo=True,
    )

    empleado_2 = Empleado(
        id_empleado=2,
        nombre="Luis",
        apellido="Martinez",
        telefono="444444444",
        activo=True,
    )

    db.add_all([
        negocio,
        cliente_1,
        cliente_2,
        servicio_1,
        servicio_2,
        estado,
        empleado_1,
        empleado_2,
    ])
    db.commit()

    return {
        "negocio": negocio,
        "cliente_1": cliente_1,
        "cliente_2": cliente_2,
        "servicio_1": servicio_1,
        "servicio_2": servicio_2,
        "estado": estado,
        "empleado_1": empleado_1,
        "empleado_2": empleado_2,
    }


def test_listar_turnos_vacio(client, datos_base):
    response = client.get("/api/turnos/")
    assert response.status_code == 200
    assert response.json() == []


def test_crear_turno_ok_con_fecha_fin_explicita(client, datos_base):
    payload = {
        "id_negocio": 1,
        "id_cliente": 1,
        "id_servicio": 1,
        "id_estado": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": "2026-04-10T10:00:00",
        "fecha_hora_fin": "2026-04-10T10:30:00",
    }

    response = client.post("/api/turnos/", json=payload)

    assert response.status_code in (200, 201)
    body = response.json()

    assert body["id_negocio"] == 1
    assert body["id_cliente"] == 1
    assert body["id_servicio"] == 1
    assert body["id_estado"] == 1
    assert body["id_empleado"] == 1
    assert body["fecha_hora_inicio"].startswith("2026-04-10T10:00:00")
    assert body["fecha_hora_fin"].startswith("2026-04-10T10:30:00")


def test_crear_turno_calcula_fecha_fin_si_no_viene(client, datos_base):
    payload = {
        "id_negocio": 1,
        "id_cliente": 1,
        "id_servicio": 1,  # duracion_min = 30
        "id_estado": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": "2026-04-10T10:00:00",
    }

    response = client.post("/api/turnos/", json=payload)

    assert response.status_code in (200, 201)
    body = response.json()

    assert body["fecha_hora_inicio"].startswith("2026-04-10T10:00:00")
    assert body["fecha_hora_fin"].startswith("2026-04-10T10:30:00")


def test_crear_turno_falla_si_no_envia_id_empleado(client, datos_base):
    payload = {
        "id_negocio": 1,
        "id_cliente": 1,
        "id_servicio": 1,
        "id_estado": 1,
        "fecha_hora_inicio": "2026-04-10T10:00:00",
    }

    response = client.post("/api/turnos/", json=payload)

    assert response.status_code == 422


def test_crear_turno_falla_si_servicio_no_existe(client, datos_base):
    payload = {
        "id_negocio": 1,
        "id_cliente": 1,
        "id_servicio": 999,
        "id_estado": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": "2026-04-10T10:00:00",
    }

    response = client.post("/api/turnos/", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "El servicio no existe"


def test_crear_turno_falla_rango_invalido(client, datos_base):
    payload = {
        "id_negocio": 1,
        "id_cliente": 1,
        "id_servicio": 1,
        "id_estado": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": "2026-04-10T10:00:00",
        "fecha_hora_fin": "2026-04-10T10:00:00",
    }

    response = client.post("/api/turnos/", json=payload)

    assert response.status_code == 422


def test_crear_turno_no_permite_superposicion_exacta(client, datos_base):
    payload_1 = {
        "id_negocio": 1,
        "id_cliente": 1,
        "id_servicio": 1,
        "id_estado": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": "2026-04-10T10:00:00",
        "fecha_hora_fin": "2026-04-10T10:30:00",
    }

    payload_2 = {
        "id_negocio": 1,
        "id_cliente": 2,
        "id_servicio": 1,
        "id_estado": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": "2026-04-10T10:00:00",
        "fecha_hora_fin": "2026-04-10T10:30:00",
    }

    r1 = client.post("/api/turnos/", json=payload_1)
    r2 = client.post("/api/turnos/", json=payload_2)

    assert r1.status_code in (200, 201)
    assert r2.status_code == 409
    assert r2.json()["detail"] == "El empleado ya tiene un turno en ese horario"


def test_crear_turno_no_permite_superposicion_parcial(client, datos_base):
    payload_1 = {
        "id_negocio": 1,
        "id_cliente": 1,
        "id_servicio": 1,
        "id_estado": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": "2026-04-10T10:00:00",
        "fecha_hora_fin": "2026-04-10T10:30:00",
    }

    payload_2 = {
        "id_negocio": 1,
        "id_cliente": 2,
        "id_servicio": 1,
        "id_estado": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": "2026-04-10T10:15:00",
        "fecha_hora_fin": "2026-04-10T10:45:00",
    }

    r1 = client.post("/api/turnos/", json=payload_1)
    r2 = client.post("/api/turnos/", json=payload_2)

    assert r1.status_code in (200, 201)
    assert r2.status_code == 409
    assert r2.json()["detail"] == "El empleado ya tiene un turno en ese horario"


def test_crear_turno_permite_turnos_contiguos(client, datos_base):
    payload_1 = {
        "id_negocio": 1,
        "id_cliente": 1,
        "id_servicio": 1,
        "id_estado": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": "2026-04-10T10:00:00",
        "fecha_hora_fin": "2026-04-10T10:30:00",
    }

    payload_2 = {
        "id_negocio": 1,
        "id_cliente": 2,
        "id_servicio": 1,
        "id_estado": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": "2026-04-10T10:30:00",
        "fecha_hora_fin": "2026-04-10T11:00:00",
    }

    r1 = client.post("/api/turnos/", json=payload_1)
    r2 = client.post("/api/turnos/", json=payload_2)

    assert r1.status_code in (200, 201)
    assert r2.status_code in (200, 201)


def test_obtener_turno_por_id_ok(client, datos_base):
    payload = {
        "id_negocio": 1,
        "id_cliente": 1,
        "id_servicio": 1,
        "id_estado": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": "2026-04-10T10:00:00",
        "fecha_hora_fin": "2026-04-10T10:30:00",
    }

    create_response = client.post("/api/turnos/", json=payload)
    assert create_response.status_code in (200, 201)

    turno_id = create_response.json()["id_turno"]

    response = client.get(f"/api/turnos/{turno_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id_turno"] == turno_id
    assert body["id_empleado"] == 1


def test_obtener_turno_inexistente_devuelve_404(client, datos_base):
    response = client.get("/api/turnos/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Turno no encontrado"


def test_actualizar_turno_ok(client, datos_base):
    payload = {
        "id_negocio": 1,
        "id_cliente": 1,
        "id_servicio": 1,
        "id_estado": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": "2026-04-10T10:00:00",
        "fecha_hora_fin": "2026-04-10T10:30:00",
    }

    create_response = client.post("/api/turnos/", json=payload)
    assert create_response.status_code in (200, 201)

    turno_id = create_response.json()["id_turno"]

    update_payload = {
        "fecha_hora_inicio": "2026-04-10T11:00:00",
        "fecha_hora_fin": "2026-04-10T11:30:00",
    }

    response = client.put(f"/api/turnos/{turno_id}", json=update_payload)

    assert response.status_code == 200
    body = response.json()
    assert body["id_turno"] == turno_id
    assert body["fecha_hora_inicio"].startswith("2026-04-10T11:00:00")
    assert body["fecha_hora_fin"].startswith("2026-04-10T11:30:00")


def test_actualizar_turno_no_permite_superposicion(client, datos_base):
    payload_1 = {
        "id_negocio": 1,
        "id_cliente": 1,
        "id_servicio": 1,
        "id_estado": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": "2026-04-10T10:00:00",
        "fecha_hora_fin": "2026-04-10T10:30:00",
    }

    payload_2 = {
        "id_negocio": 1,
        "id_cliente": 2,
        "id_servicio": 1,
        "id_estado": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": "2026-04-10T11:00:00",
        "fecha_hora_fin": "2026-04-10T11:30:00",
    }

    r1 = client.post("/api/turnos/", json=payload_1)
    r2 = client.post("/api/turnos/", json=payload_2)

    assert r1.status_code in (200, 201)
    assert r2.status_code in (200, 201)

    turno_2_id = r2.json()["id_turno"]

    update_payload = {
        "fecha_hora_inicio": "2026-04-10T10:15:00",
        "fecha_hora_fin": "2026-04-10T10:45:00",
    }

    response = client.put(f"/api/turnos/{turno_2_id}", json=update_payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "El empleado ya tiene un turno en ese horario"


def test_actualizar_turno_permite_cambiar_empleado_si_no_hay_conflicto(client, datos_base):
    payload = {
        "id_negocio": 1,
        "id_cliente": 1,
        "id_servicio": 1,
        "id_estado": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": "2026-04-10T10:00:00",
        "fecha_hora_fin": "2026-04-10T10:30:00",
    }

    create_response = client.post("/api/turnos/", json=payload)
    assert create_response.status_code in (200, 201)

    turno_id = create_response.json()["id_turno"]

    update_payload = {
        "id_empleado": 2
    }

    response = client.put(f"/api/turnos/{turno_id}", json=update_payload)

    assert response.status_code == 200
    assert response.json()["id_empleado"] == 2


def test_actualizar_turno_inexistente_devuelve_404(client, datos_base):
    response = client.put(
        "/api/turnos/9999",
        json={"fecha_hora_inicio": "2026-04-10T11:00:00"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Turno no encontrado"


def test_borrar_turno_ok(client, datos_base):
    payload = {
        "id_negocio": 1,
        "id_cliente": 1,
        "id_servicio": 1,
        "id_estado": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": "2026-04-10T10:00:00",
        "fecha_hora_fin": "2026-04-10T10:30:00",
    }

    create_response = client.post("/api/turnos/", json=payload)
    assert create_response.status_code in (200, 201)

    turno_id = create_response.json()["id_turno"]

    response = client.delete(f"/api/turnos/{turno_id}")

    assert response.status_code == 200
    assert response.json()["mensaje"] == "Turno eliminado"

    get_response = client.get(f"/api/turnos/{turno_id}")
    assert get_response.status_code == 404


def test_borrar_turno_inexistente_devuelve_404(client, datos_base):
    response = client.delete("/api/turnos/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Turno no encontrado"

