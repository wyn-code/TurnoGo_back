from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.schemas.categoria_schema import CategoriaCreate, CategoriaUpdate


def listar_categorias(db: Session):
    return db.query(Categoria).order_by(Categoria.nombre).all()


def obtener_categoria_por_id(db: Session, categoria_id: int):
    return (
        db.query(Categoria).filter(Categoria.id_categoria == categoria_id).first()
    )


def crear_categoria(db: Session, data: CategoriaCreate) -> Categoria:
    row = Categoria(nombre=data.nombre, icono=data.icono)
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
    if data.nombre is not None:
        row.nombre = data.nombre
    if data.icono is not None:
        row.icono = data.icono
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
