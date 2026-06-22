def test_crear_categoria_con_icono_url_y_descripcion(client):
    data = {
        "nombre": "Barberia",
        "icono": "https://example.com/barberia.jpg",
        "descripcion": "Cortes masculinos y barba",
    }

    response = client.post("/api/categorias/", json=data)

    assert response.status_code == 200
    body = response.json()
    assert body["id_categoria"]
    assert body["nombre"] == data["nombre"]
    assert body["icono"] == data["icono"]
    assert body["descripcion"] == data["descripcion"]


def test_listar_categorias_ordenadas_por_nombre(client):
    client.post(
        "/api/categorias/",
        json={
            "nombre": "Unas",
            "icono": "https://example.com/unas.png",
            "descripcion": "Manicuria",
        },
    )
    client.post(
        "/api/categorias/",
        json={
            "nombre": "Barberia",
            "icono": "https://example.com/barberia.jpg",
            "descripcion": "Barba",
        },
    )

    response = client.get("/api/categorias/")

    assert response.status_code == 200
    nombres = [categoria["nombre"] for categoria in response.json()]
    assert nombres == sorted(nombres)


def test_actualizar_categoria_permite_limpiar_icono_y_descripcion(client):
    created = client.post(
        "/api/categorias/",
        json={
            "nombre": "Masajes",
            "icono": "https://example.com/masajes.webp",
            "descripcion": "Masajes relajantes",
        },
    ).json()

    response = client.put(
        f"/api/categorias/{created['id_categoria']}",
        json={"icono": None, "descripcion": ""},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["icono"] is None
    assert body["descripcion"] is None


def test_rechaza_url_no_http(client):
    response = client.post(
        "/api/categorias/",
        json={
            "nombre": "Estetica",
            "icono": "ftp://example.com/estetica.jpg",
            "descripcion": "Tratamientos de belleza",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "icono debe ser una URL http(s) valida"
