def test_listar_negocios_vacio(client):
    response = client.get("/api/negocios/")
    assert response.status_code == 200
    assert response.json() == []


def test_traer_negocio_inexistente_por_id(client):
    response = client.get("/api/negocios/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Negocio no encontrado"}


def test_traer_negocio_inexistente_por_slug(client):
    response = client.get("/api/negocios/slug/no-existe")
    assert response.status_code == 404
    assert response.json() == {"detail": "Negocio no encontrado"}


def test_crear_negocio(client, seed_data):
    data = {
        "nombre": "Barberia Rocco",
        "wsp": "3364000000",
        "telefono": "3364000000",
        "direccion": "Mitre 123",
        "ciudad": "San Nicolas",
        "slug": "barberia-rocco",
        "activo": True,
        "usuario_id": 2,
        "id_categoria": 1,
    }

    response = client.post("/api/negocios/", json=data)
    assert response.status_code in [200, 201], response.text

    body = response.json()
    assert body["nombre"] == data["nombre"]
    assert body["wsp"] == data["wsp"]
    assert body["telefono"] == data["telefono"]
    assert body["direccion"] == data["direccion"]
    assert body["ciudad"] == data["ciudad"]
    assert body["activo"] == data["activo"]


def test_listar_negocios_con_un_registro(client, seed_data):
    data = {
        "nombre": "Negocio Test",
        "wsp": "3364111111",
        "telefono": "3364111111",
        "direccion": "Belgrano 456",
        "ciudad": "San Nicolas",
        "slug": "negocio-test",
        "activo": True,
        "usuario_id": 2,
        "id_categoria": 1,
    }

    create_response = client.post("/api/negocios/", json=data)
    assert create_response.status_code in [200, 201], create_response.text

    list_response = client.get("/api/negocios/")
    assert list_response.status_code == 200

    negocios = list_response.json()
    assert len(negocios) >= 1
    assert any(n["nombre"] == "Negocio Test" for n in negocios)


def test_traer_negocio_por_id(client, seed_data):
    data = {
        "nombre": "Negocio ID Test",
        "wsp": "3364222222",
        "telefono": "3364222222",
        "direccion": "Test 123",
        "ciudad": "San Nicolas",
        "slug": "negocio-id-test",
        "activo": True,
        "usuario_id": 2,
        "id_categoria": 1,
    }

    create_response = client.post("/api/negocios/", json=data)
    assert create_response.status_code in [200, 201], create_response.text

    negocio_creado = create_response.json()
    negocio_id = negocio_creado["id_negocio"]

    get_response = client.get(f"/api/negocios/{negocio_id}")
    assert get_response.status_code == 200

    body = get_response.json()
    assert body["id_negocio"] == negocio_id
    assert body["nombre"] == data["nombre"]


def test_traer_negocio_por_slug(client, seed_data):
    data = {
        "nombre": "Negocio Slug Test",
        "wsp": "3364333333",
        "telefono": "3364333333",
        "direccion": "Slug 123",
        "ciudad": "San Nicolas",
        "slug": "negocio-slug-test",
        "activo": True,
        "usuario_id": 2,
        "id_categoria": 1,
    }

    create_response = client.post("/api/negocios/", json=data)
    assert create_response.status_code in [200, 201], create_response.text

    get_response = client.get("/api/negocios/slug/negocio-slug-test")
    assert get_response.status_code == 200

    body = get_response.json()
    print(body)

    assert body["nombre"] == data["nombre"]
    assert body["slug"] == "negocio-slug-test"