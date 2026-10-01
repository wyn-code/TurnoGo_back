from sqlalchemy import func
from sqlalchemy.orm import Session
from urllib.parse import urlparse

from app.models.categoria import Categoria
from app.models.negocio import Negocio
from app.schemas.categoria_schema import CategoriaCreate, CategoriaUpdate


IMAGE_URL_EXTENSIONS = (
    ".avif",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".svg",
    ".webp",
)


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _validate_image_url(value: str | None) -> None:
    if value is None:
        return

    normalized = value.lower()
    if "://" not in normalized:
        return

    if not normalized.startswith(("http://", "https://")):
        raise ValueError("icono debe ser una URL http(s) valida")

    path = urlparse(value).path.lower()
    if "." in path and not path.endswith(IMAGE_URL_EXTENSIONS):
        raise ValueError("icono debe apuntar a una imagen valida")


def _normalize_nombre(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("nombre es obligatorio")
    return value


def _validar_parent(
    db: Session, parent_id: int | None, categoria_id: int | None = None
) -> None:
    """El padre debe existir y no puede ser la propia categoría ni un descendiente."""
    if parent_id is None:
        return
    if categoria_id is not None and parent_id in ids_con_descendientes(db, categoria_id):
        raise ValueError("parent_id genera un ciclo en el árbol de categorías")
    if not obtener_categoria_por_id(db, parent_id):
        raise ValueError("parent_id no existe")


def ids_con_descendientes(db: Session, categoria_id: int) -> set[int]:
    """Id de la categoría más los de todos sus descendientes (cualquier nivel)."""
    hijos_por_padre: dict[int, list[int]] = {}
    for id_categoria, parent_id in db.query(
        Categoria.id_categoria, Categoria.parent_id
    ).filter(Categoria.parent_id.is_not(None)):
        hijos_por_padre.setdefault(parent_id, []).append(id_categoria)

    ids, pendientes = {categoria_id}, [categoria_id]
    while pendientes:
        for hijo in hijos_por_padre.get(pendientes.pop(), []):
            if hijo not in ids:
                ids.add(hijo)
                pendientes.append(hijo)
    return ids


def arbol_categorias(db: Session) -> list[dict]:
    """Árbol completo: raíces ordenadas por nombre, cada una con sus hijos."""
    filas = db.query(Categoria).order_by(Categoria.nombre).all()
    nodos = {
        c.id_categoria: {
            "id_categoria": c.id_categoria,
            "nombre": c.nombre,
            "icono": c.icono,
            "descripcion": c.descripcion,
            "parent_id": c.parent_id,
            "children": [],
        }
        for c in filas
    }
    raices = []
    for c in filas:
        nodo = nodos[c.id_categoria]
        padre = nodos.get(c.parent_id) if c.parent_id is not None else None
        (padre["children"] if padre else raices).append(nodo)
    return raices


def categorias_top(db: Session, limit: int = 5) -> list[dict]:
    """Las categorías con más negocios activos, de mayor a menor.

    Cuenta negocios cuyo `id_categoria` es exactamente la categoría (un negocio
    siempre cuelga de una hoja) y omite las categorías sin negocios activos.
    """
    cantidad = func.count(Negocio.id_negocio).label("cantidad_negocios")
    filas = (
        db.query(Categoria, cantidad)
        .join(Negocio, Negocio.id_categoria == Categoria.id_categoria)
        .filter(Negocio.activo.is_(True))
        .group_by(Categoria.id_categoria)
        .order_by(cantidad.desc(), Categoria.nombre)
        .limit(limit)
        .all()
    )
    return [
        {
            "id_categoria": c.id_categoria,
            "nombre": c.nombre,
            "icono": c.icono,
            "descripcion": c.descripcion,
            "parent_id": c.parent_id,
            "cantidad_negocios": n,
        }
        for c, n in filas
    ]


def listar_categorias(db: Session) -> list[Categoria]:
    return db.query(Categoria).order_by(Categoria.nombre).all()


def obtener_categoria_por_id(db: Session, categoria_id: int) -> Categoria | None:
    return (
        db.query(Categoria).filter(Categoria.id_categoria == categoria_id).first()
    )


def crear_categoria(db: Session, data: CategoriaCreate) -> Categoria:
    icono = _normalize_optional_text(data.icono)
    descripcion = _normalize_optional_text(data.descripcion)
    _validate_image_url(icono)
    _validar_parent(db, data.parent_id)

    row = Categoria(
        nombre=_normalize_nombre(data.nombre),
        icono=icono,
        descripcion=descripcion,
        parent_id=data.parent_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def actualizar_categoria(
    db: Session, categoria_id: int, data: CategoriaUpdate
) -> Categoria | None:
    row = obtener_categoria_por_id(db, categoria_id)
    if not row:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if "nombre" in update_data and update_data["nombre"] is not None:
        row.nombre = _normalize_nombre(update_data["nombre"])
    if "icono" in update_data:
        icono = _normalize_optional_text(update_data["icono"])
        _validate_image_url(icono)
        row.icono = icono
    if "descripcion" in update_data:
        row.descripcion = _normalize_optional_text(update_data["descripcion"])
    if "parent_id" in update_data:
        _validar_parent(db, update_data["parent_id"], categoria_id)
        row.parent_id = update_data["parent_id"]

    db.commit()
    db.refresh(row)
    return row


def borrar_categoria(db: Session, categoria_id: int) -> Categoria | None:
    row = obtener_categoria_por_id(db, categoria_id)
    if not row:
        return None
    if row.children:
        raise ValueError("No se puede borrar una categoría con sub-categorías")
    db.delete(row)
    db.commit()
    return row
