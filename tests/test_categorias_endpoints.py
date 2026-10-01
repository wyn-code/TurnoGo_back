"""Categorías jerárquicas: GET /categorias/tree y validación de parent_id."""

import pytest

from app.models.categoria import Categoria
from tests.test_categorias import _admin_headers


@pytest.fixture()
def jerarquia(db):
    """Deportes (Fútbol, Pádel) y Belleza (raíz sin hijos)."""
    deportes = Categoria(nombre="Deportes")
    belleza = Categoria(nombre="Belleza")
    db.add_all([deportes, belleza])
    db.flush()
    db.add_all([
        Categoria(nombre="Pádel", parent_id=deportes.id_categoria),
        Categoria(nombre="Fútbol", parent_id=deportes.id_categoria),
    ])
    db.commit()
    return {"deportes": deportes, "belleza": belleza}


def test_tree_devuelve_padres_con_hijos_anidados(client, jerarquia):
    res = client.get("/api/categorias/tree")
    assert res.status_code == 200

    arbol = res.json()
    assert [c["nombre"] for c in arbol] == ["Belleza", "Deportes"]

    deportes = next(c for c in arbol if c["nombre"] == "Deportes")
    assert [h["nombre"] for h in deportes["children"]] == ["Fútbol", "Pádel"]
    assert all(h["parent_id"] == deportes["id_categoria"] for h in deportes["children"])
    assert deportes["parent_id"] is None
    assert next(c for c in arbol if c["nombre"] == "Belleza")["children"] == []


def test_tree_no_repite_hijos_como_raices(client, jerarquia):
    arbol = client.get("/api/categorias/tree").json()
    assert "Fútbol" not in [c["nombre"] for c in arbol]


def test_tree_es_publico_y_vacio_sin_categorias(client):
    res = client.get("/api/categorias/tree")
    assert res.status_code == 200
    assert res.json() == []


def test_listado_plano_incluye_parent_id(client, jerarquia):
    filas = {c["nombre"]: c for c in client.get("/api/categorias/").json()}
    assert filas["Fútbol"]["parent_id"] == jerarquia["deportes"].id_categoria
    assert filas["Deportes"]["parent_id"] is None


def test_crear_subcategoria_con_parent_id(client, db, jerarquia):
    res = client.post(
        "/api/categorias/",
        json={"nombre": "Tenis", "parent_id": jerarquia["deportes"].id_categoria},
        headers=_admin_headers(client, db),
    )
    assert res.status_code == 200, res.text
    assert res.json()["parent_id"] == jerarquia["deportes"].id_categoria


def test_parent_id_inexistente_da_400(client, db):
    res = client.post(
        "/api/categorias/",
        json={"nombre": "Huérfana", "parent_id": 9999},
        headers=_admin_headers(client, db),
    )
    assert res.status_code == 400


def test_no_permite_ciclos(client, db, jerarquia):
    headers = _admin_headers(client, db)
    deportes = jerarquia["deportes"].id_categoria
    futbol = db.query(Categoria).filter(Categoria.nombre == "Fútbol").one().id_categoria

    # Una categoría no puede ser su propio padre, ni colgar de un descendiente.
    assert client.put(
        f"/api/categorias/{deportes}", json={"parent_id": deportes}, headers=headers
    ).status_code == 400
    assert client.put(
        f"/api/categorias/{deportes}", json={"parent_id": futbol}, headers=headers
    ).status_code == 400


def test_mover_y_desvincular_subcategoria(client, db, jerarquia):
    headers = _admin_headers(client, db)
    futbol = db.query(Categoria).filter(Categoria.nombre == "Fútbol").one().id_categoria

    res = client.put(
        f"/api/categorias/{futbol}",
        json={"parent_id": jerarquia["belleza"].id_categoria},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["parent_id"] == jerarquia["belleza"].id_categoria

    res = client.put(f"/api/categorias/{futbol}", json={"parent_id": None}, headers=headers)
    assert res.json()["parent_id"] is None


def test_no_se_borra_categoria_con_hijos(client, db, jerarquia):
    res = client.delete(
        f"/api/categorias/{jerarquia['deportes'].id_categoria}",
        headers=_admin_headers(client, db),
    )
    assert res.status_code == 409
    assert db.query(Categoria).filter(Categoria.nombre == "Fútbol").count() == 1


def test_tree_con_estructura_final_de_deportes(client, db):
    """Deportes con exactamente sus 3 canchas; el resto son raíces con children vacío."""
    deportes = Categoria(nombre="Deportes")
    db.add_all([deportes, Categoria(nombre="Barberia"), Categoria(nombre="Básquet"),
                Categoria(nombre="Peluqueria")])
    db.flush()
    db.add_all([Categoria(nombre=n, parent_id=deportes.id_categoria)
                for n in ("Cancha de Futbol", "Cancha de Padel", "Cancha de Tenis")])
    db.commit()

    arbol = {c["nombre"]: c for c in client.get("/api/categorias/tree").json()}

    assert set(arbol) == {"Barberia", "Básquet", "Deportes", "Peluqueria"}
    assert [h["nombre"] for h in arbol["Deportes"]["children"]] == [
        "Cancha de Futbol", "Cancha de Padel", "Cancha de Tenis"]
    for simple in ("Barberia", "Básquet", "Peluqueria"):
        assert arbol[simple]["children"] == []


# ── GET /categorias/top ──


_seq = iter(range(1, 1000))


def _negocio(db, categoria, activo=True, nombre=None):
    """Negocio con su propio usuario (usuario_id es único por negocio)."""
    from app.core.security import get_password_hash
    from app.models.negocio import Negocio
    from app.models.usuario import Usuario

    i = next(_seq)
    db.add(Usuario(usuario_us=f"u{i}", email_us=f"u{i}@t.com",
                   contrasena_us=get_password_hash("Test1234567!")))
    db.flush()
    uid = db.query(Usuario).filter(Usuario.usuario_us == f"u{i}").one().id_us
    db.add(Negocio(usuario_id=uid, nombre=nombre or f"N{i}", id_categoria=categoria.id_categoria,
                   wsp="1", direccion="x", ciudad="y", slug=f"n{i}", activo=activo))


@pytest.fixture()
def con_negocios(db):
    """6 categorías con 5,4,3,2,1 y 0 negocios activos (+1 negocio inactivo en la última)."""
    cats = [Categoria(nombre=n) for n in ["Cinco", "Cuatro", "Tres", "Dos", "Uno", "Vacia"]]
    db.add_all(cats)
    db.flush()
    for cat, cantidad in zip(cats, [5, 4, 3, 2, 1, 0]):
        for _ in range(cantidad):
            _negocio(db, cat)
    _negocio(db, cats[5], activo=False, nombre="Cerrado")
    db.commit()


def test_top_devuelve_5_ordenadas_por_cantidad_desc(client, con_negocios):
    res = client.get("/api/categorias/top?limit=5")
    assert res.status_code == 200
    top = res.json()
    assert [c["nombre"] for c in top] == ["Cinco", "Cuatro", "Tres", "Dos", "Uno"]
    assert [c["cantidad_negocios"] for c in top] == [5, 4, 3, 2, 1]


def test_top_nunca_incluye_categorias_sin_negocios_activos(client, con_negocios):
    # "Vacia" sólo tiene un negocio inactivo: no cuenta.
    nombres = [c["nombre"] for c in client.get("/api/categorias/top?limit=50").json()]
    assert "Vacia" not in nombres
    assert len(nombres) == 5


def test_top_limit_es_parametrizable_y_por_defecto_5(client, con_negocios):
    assert [c["nombre"] for c in client.get("/api/categorias/top?limit=3").json()] == [
        "Cinco", "Cuatro", "Tres"]
    assert len(client.get("/api/categorias/top").json()) == 5


def test_top_valida_el_limit(client, con_negocios):
    assert client.get("/api/categorias/top?limit=0").status_code == 422
    assert client.get("/api/categorias/top?limit=999").status_code == 422


def test_top_incluye_id_y_parent_para_navegar_por_la_subcategoria(client, db):
    padre = Categoria(nombre="Deportes")
    db.add(padre)
    db.flush()
    hija = Categoria(nombre="Cancha de Padel", parent_id=padre.id_categoria)
    db.add(hija)
    db.flush()
    _negocio(db, hija, nombre="El Galpon")
    db.commit()

    top = client.get("/api/categorias/top").json()
    assert [(c["nombre"], c["id_categoria"], c["parent_id"]) for c in top] == [
        ("Cancha de Padel", hija.id_categoria, padre.id_categoria)]  # el padre vacío no aparece


def test_basquet_y_voley_no_aparecen_en_el_listado(client):
    nombres = [c["nombre"] for c in client.get("/api/categorias/").json()]
    assert not {"Básquet", "Basquet", "Vóley", "Voley"} & set(nombres)
