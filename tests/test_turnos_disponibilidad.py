from datetime import datetime, timedelta
from fastapi.testclient import TestClient


def crear_cliente(client: TestClient, telefono: str, nombre="Rocco", apellido="Lavecchia"):
    res = client.post(
        "/api/clientes/get-or-create",
        json={
            "telefono": telefono,
            "nombre": nombre,
            "apellido": apellido,
        },
    )
    assert res.status_code == 200, res.text
    return res.json()


def test_get_or_create_reutiliza_cliente(client: TestClient):
    cliente_1 = crear_cliente(client, "3364123456")
    cliente_2 = crear_cliente(client, "3364123456")

    assert cliente_1["id_cliente"] == cliente_2["id_cliente"]
    assert cliente_1["telefono"] == "3364123456"


def test_crear_turno_y_rechazar_superposicion(client: TestClient, seed_data):
    cliente = crear_cliente(client, "3364999000")

    inicio = datetime(2026, 4, 20, 10, 0, 0)

    payload_1 = {
        "id_negocio": 1,
        "id_cliente": cliente["id_cliente"],
        "id_servicio": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": inicio.isoformat(),
    }

    res_1 = client.post("/api/turnos/", json=payload_1)
    assert res_1.status_code == 201, res_1.text
    turno_1 = res_1.json()

    assert turno_1["id_negocio"] == 1
    assert turno_1["id_cliente"] == cliente["id_cliente"]
    assert turno_1["id_servicio"] == 1
    assert turno_1["id_empleado"] == 1
    assert turno_1["fecha_hora_fin"] is not None

    payload_superpuesto = {
        "id_negocio": 1,
        "id_cliente": cliente["id_cliente"],
        "id_servicio": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": (inicio + timedelta(minutes=15)).isoformat(),
    }

    res_2 = client.post("/api/turnos/", json=payload_superpuesto)
    assert res_2.status_code == 409, res_2.text
    assert "horario" in res_2.json()["detail"].lower()


def test_permite_turno_no_superpuesto(client: TestClient, seed_data):
    cliente = crear_cliente(client, "3364888000")

    inicio_1 = datetime(2026, 4, 21, 10, 0, 0)
    inicio_2 = datetime(2026, 4, 21, 10, 30, 0)

    payload_1 = {
        "id_negocio": 1,
        "id_cliente": cliente["id_cliente"],
        "id_servicio": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": inicio_1.isoformat(),
    }

    res_1 = client.post("/api/turnos/", json=payload_1)
    assert res_1.status_code == 201, res_1.text

    payload_2 = {
        "id_negocio": 1,
        "id_cliente": cliente["id_cliente"],
        "id_servicio": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": inicio_2.isoformat(),
    }

    res_2 = client.post("/api/turnos/", json=payload_2)
    assert res_2.status_code == 201, res_2.text


def test_listar_turnos_por_rango(client: TestClient, seed_data):
    res = client.get(
        "/api/turnos/por-rango",
        params={
            "id_negocio": 1,
            "desde": "2026-04-01T00:00:00",
            "hasta": "2026-05-01T00:00:00",
            "id_empleado": 1,
        },
    )

    assert res.status_code == 200, res.text
    data = res.json()
    assert isinstance(data, list)