"""CRUD de espacios (ex canchas) y compatibilidad con las rutas /canchas."""

from tests.auth_helpers import obtener_token


def _duenio(client):
    return obtener_token(client, "test1@test.com", "Test1234567!")


def _ajeno(client):
    return obtener_token(client, "test2@test.com", "Test1234567!")


def _crear(client, id_negocio, nombre="Cancha 1", headers=None, **extra):
    return client.post(
        "/api/espacios",
        json={"id_negocio": id_negocio, "nombre": nombre, **extra},
        headers=headers if headers is not None else _duenio(client),
    )


def test_crear_espacio_devuelve_201_con_campos_nuevos(client, seed_data):
    res = _crear(client, 1, "Cancha 5", numero=5, descripcion="Techada")
    assert res.status_code == 201, res.text
    body = res.json()
    assert (body["nombre"], body["numero"], body["descripcion"]) == ("Cancha 5", 5, "Techada")
    assert body["id_negocio"] == 1 and body["activo"] is True
    assert body["id_cancha"] == body["id_espacio"]  # alias legado


def test_un_negocio_puede_tener_varios_espacios(client, seed_data):
    _crear(client, 1, "A", numero=2)
    _crear(client, 1, "B", numero=1)
    lista = client.get("/api/negocios/1/espacios").json()
    assert [e["nombre"] for e in lista] == ["B", "A"]  # ordenados por numero


def test_listado_es_publico_y_oculta_inactivos(client, seed_data):
    id_espacio = _crear(client, 1, "Vieja").json()["id_espacio"]
    client.delete(f"/api/espacios/{id_espacio}", headers=_duenio(client))

    assert client.get("/api/negocios/1/espacios").json() == []
    todos = client.get("/api/negocios/1/espacios?incluir_inactivas=true").json()
    assert [e["id_espacio"] for e in todos] == [id_espacio]


def test_crear_exige_autenticacion(client, seed_data):
    res = client.post("/api/espacios", json={"id_negocio": 1, "nombre": "X"})
    assert res.status_code in (401, 403)


def test_fk_negocio_inexistente_da_404(client, seed_data):
    assert _crear(client, 9999).status_code == 404


def test_negocio_ajeno_da_403(client, seed_data):
    assert _crear(client, 1, headers=_ajeno(client)).status_code == 403


def test_actualizar_espacio(client, seed_data):
    id_espacio = _crear(client, 1, "Vieja").json()["id_espacio"]
    res = client.put(
        f"/api/espacios/{id_espacio}",
        json={"nombre": " Nueva ", "numero": 3, "descripcion": "Muy linda"},
        headers=_duenio(client),
    )
    assert res.status_code == 200, res.text
    assert (res.json()["nombre"], res.json()["numero"]) == ("Nueva", 3)


def test_actualizar_y_borrar_de_otro_negocio_da_403(client, seed_data):
    id_espacio = _crear(client, 1).json()["id_espacio"]
    assert client.put(
        f"/api/espacios/{id_espacio}", json={"nombre": "Hack"}, headers=_ajeno(client)
    ).status_code == 403
    assert client.delete(f"/api/espacios/{id_espacio}", headers=_ajeno(client)).status_code == 403


def test_espacio_inexistente_da_404(client, seed_data):
    assert client.delete("/api/espacios/9999", headers=_duenio(client)).status_code == 404


def test_nombre_vacio_da_422(client, seed_data):
    assert _crear(client, 1, "").status_code == 422


def test_espacios_se_borran_con_el_negocio(client, db, seed_data):
    from app.models.espacio import Espacio
    from app.models.negocio import Negocio

    _crear(client, 1)
    db.expire_all()
    db.delete(db.get(Negocio, 1))
    db.commit()
    assert db.query(Espacio).filter(Espacio.id_negocio == 1).count() == 0


def test_rutas_legadas_de_canchas_siguen_funcionando(client, seed_data):
    creada = client.post(
        "/api/canchas/negocio/1", json={"nombre": "Legada"}, headers=_duenio(client)
    )
    assert creada.status_code == 201
    id_cancha = creada.json()["id_cancha"]

    # Lo creado por la ruta vieja se ve por la nueva y viceversa.
    assert [e["id_espacio"] for e in client.get("/api/negocios/1/espacios").json()] == [id_cancha]
    assert client.get("/api/canchas/negocio/1").json()[0]["id_espacio"] == id_cancha
