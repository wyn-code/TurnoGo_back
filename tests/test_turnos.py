
from fastapi.testclient import TestClient

# 1. DUEÑO PUEDE EDITAR SU NEGOCIO (Este estaba bien)
def test_owner_puede_editar_su_negocio(client, seed_data):
    from .auth import obtener_token

    # Usamos test1 porque ES el dueño (usuario_id=1)
    headers = obtener_token(
        client,
        "test1@test.com",
        "123456"
    )

    payload = {
        "nombre": "Negocio Editado"
    }

    response = client.put(
        f"/api/negocios/{seed_data['negocio'].id_negocio}",
        json=payload,
        headers=headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["nombre"] == "Negocio Editado"


# 2. DUEÑO NO PUEDE EDITAR NEGOCIO AJENO
def test_owner_no_puede_editar_negocio_ajeno(client, seed_data):
    from .auth import obtener_token

    # Usamos test2 porque NO es el dueño
    headers = obtener_token(
        client,
        "test2@test.com", 
        "123456"
    )
    payload = {
        "nombre": "Negocio Hackeado" 
    }
    response = client.put(
        f"/api/negocios/{seed_data['negocio'].id_negocio}",
        json=payload,
        headers=headers
    )
    assert response.status_code == 403


# 3. NO PUEDE BORRAR NEGOCIO AJENO
def test_owner_no_puede_borrar_negocio_ajeno(client, seed_data):
    from .auth import obtener_token

    # Usamos test2
    headers = obtener_token(
        client,
        "test2@test.com",
        "123456"
    )
    response = client.delete(
        f"/api/negocios/{seed_data['negocio'].id_negocio}",
        headers=headers
    )
    assert response.status_code == 403


# 4. NO PUEDE CREAR SERVICIO EN NEGOCIO AJENO
def test_owner_no_puede_crear_servicio_en_negocio_ajeno(client, seed_data):
    from .auth import obtener_token

    # Usamos test2
    headers = obtener_token(
        client,
        "test2@test.com",
        "123456"
    )
    payload = {
        "nombre": "Servicio Test",
        "duracion_minutos": 60,
        "precio": 1000,
        "id_negocio": seed_data["negocio"].id_negocio
    }
    response = client.post(
        "/api/servicios/",
        json=payload,
        headers=headers
    )
    assert response.status_code == 403


# 5. NO PUEDE ACCEDER DASHBOARD PRIVADO AJENO
def test_owner_no_puede_acceder_dashboard_privado_ajeno(client, seed_data):
    from .auth import obtener_token

    # Usamos test2
    headers = obtener_token(
        client,
        "test2@test.com",
        "123456"
    )
    response = client.get(
        f"/api/negocios/{seed_data['negocio'].id_negocio}/dashboard",
        headers=headers
    )
    assert response.status_code == 403