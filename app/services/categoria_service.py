from sqlalchemy.orm import Session
from urllib.parse import urlparse

from app.models.categoria import Categoria
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

    row = Categoria(
        nombre=_normalize_nombre(data.nombre),
        icono=icono,
        descripcion=descripcion,
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

    db.commit()
    db.refresh(row)
    return row


def borrar_categoria(db: Session, categoria_id: int) -> Categoria | None:
    row = obtener_categoria_por_id(db, categoria_id)
    if not row:
        return None
    db.delete(row)
    db.commit()
    return row
