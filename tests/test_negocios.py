def test_listar_negocios_vacio(client):
    response = client.get("/api/negocios/")

    assert response.status_code == 200
    assert response.json() == []


def test_traer_negocio_inexistente_por_id(client):
    response = client.get("/api/negocios/id/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Negocio no encontrado"}


def test_traer_negocio_inexistente_por_slug(client):
    response = client.get("/api/negocios/slug/no-existe")

    assert response.status_code == 404
    assert response.json() == {"detail": "Negocio no encontrado"}


def test_crear_negocio(client):
    data = {
        "nombre": "Barberia Rocco",
        "rubro": "Barberia",
        "wsp": "3364000000",
        "telefono": "3364000000",
        "direccion": "Mitre 123",
        "ciudad": "San Nicolas",
        "slug": "barberia-rocco",
        "activo": True
    }

    response = client.post("/api/negocios/", json=data)

    assert response.status_code in [200, 201]

    body = response.json()
    assert body["nombre"] == data["nombre"]
    assert body["rubro"] == data["rubro"]
    assert body["wsp"] == data["wsp"]
    assert body["telefono"] == data["telefono"]
    assert body["direccion"] == data["direccion"]
    assert body["ciudad"] == data["ciudad"]
    assert body["slug"] == data["slug"]
    assert body["activo"] == data["activo"]


def test_listar_negocios_con_un_registro(client):
    data = {
        "nombre": "Negocio Test",
        "rubro": "Peluqueria",
        "wsp": "3364111111",
        "telefono": "3364111111",
        "direccion": "Belgrano 456",
        "ciudad": "San Nicolas",
        "slug": "negocio-test",
        "activo": True
    }

    create_response = client.post("/api/negocios/", json=data)
    assert create_response.status_code in [200, 201]

    list_response = client.get("/api/negocios/")
    assert list_response.status_code == 200

    negocios = list_response.json()
    assert len(negocios) == 1
    assert negocios[0]["nombre"] == "Negocio Test"
    assert negocios[0]["slug"] == "negocio-test"


def test_traer_negocio_por_id(client):
    data = {
        "nombre": "Negocio ID Test",
        "rubro": "Barberia",
        "wsp": "3364222222",
        "telefono": "3364222222",
        "direccion": "Test 123",
        "ciudad": "San Nicolas",
        "slug": "negocio-id-test",
        "activo": True
    }

    create_response = client.post("/api/negocios/", json=data)
    assert create_response.status_code in [200, 201]

    negocio_creado = create_response.json()
    negocio_id = negocio_creado["id_negocio"]

    get_response = client.get(f"/api/negocios/id/{negocio_id}")
    assert get_response.status_code == 200

    body = get_response.json()
    assert body["id_negocio"] == negocio_id
    assert body["nombre"] == data["nombre"]
    assert body["slug"] == data["slug"]


def test_traer_negocio_por_slug(client):
    data = {
        "nombre": "Negocio Slug Test",
        "rubro": "Barberia",
        "wsp": "3364333333",
        "telefono": "3364333333",
        "direccion": "Slug 123",
        "ciudad": "San Nicolas",
        "slug": "negocio-slug-test",
        "activo": True
    }

    create_response = client.post("/api/negocios/", json=data)
    assert create_response.status_code in [200, 201]

    get_response = client.get("/api/negocios/slug/negocio-slug-test")
    assert get_response.status_code == 200

    body = get_response.json()
    assert body["nombre"] == data["nombre"]
    assert body["slug"] == data["slug"]