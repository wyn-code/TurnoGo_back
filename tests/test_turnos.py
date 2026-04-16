from datetime import datetime, timedelta


def crear_cliente(client, telefono):
    res = client.post(
        "/api/clientes/get-or-create",
        json={
            "telefono": telefono,
            "nombre": "Rocco",
            "apellido": "Lavecchia",
        },
    )
    assert res.status_code == 200
    return res.json()


def test_turno_superposicion(client, seed_data):
    cliente = crear_cliente(client, "3364000000")

    inicio = datetime(2026, 4, 20, 10, 0, 0)

    payload_1 = {
        "id_negocio": 1,
        "id_cliente": cliente["id_cliente"],
        "id_servicio": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": inicio.isoformat(),
    }

    # Crear primer turno
    res_1 = client.post("/api/turnos/", json=payload_1)
    assert res_1.status_code == 201

    # Intentar superposición
    payload_2 = {
        "id_negocio": 1,
        "id_cliente": cliente["id_cliente"],
        "id_servicio": 1,
        "id_empleado": 1,
        "fecha_hora_inicio": (inicio + timedelta(minutes=15)).isoformat(),
    }

    res_2 = client.post("/api/turnos/", json=payload_2)

    assert res_2.status_code == 409
    assert "turno" in res_2.json()["detail"].lower()