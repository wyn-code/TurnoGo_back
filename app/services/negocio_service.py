from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.negocio import Negocio
from app.schemas.negocio_schema import NegocioCreate


def _query_por_slug(db: Session, slug: str):
    return db.query(Negocio).filter(Negocio.slug == slug)


def crear_negocio(db: Session, negocio_data: NegocioCreate):
    negocio_existente = _query_por_slug(db, negocio_data.slug).first()

    if negocio_existente:
        raise ValueError("Ya existe un negocio con ese slug")

    nuevo_negocio = Negocio(**negocio_data.model_dump())

    try:
        db.add(nuevo_negocio)
        db.commit()
        db.refresh(nuevo_negocio)
        return nuevo_negocio
    except IntegrityError:
        db.rollback()
        raise ValueError("Error de integridad al crear el negocio")
    except Exception:
        db.rollback()
        raise


def obtener_negocios(db: Session):
    return db.query(Negocio).all()


def obtener_negocio_por_id(db: Session, id_negocio: int):
    return (
        db.query(Negocio)
        .filter(Negocio.id_negocio == id_negocio)
        .first()
    )


def obtener_negocio_por_slug(db: Session, slug: str):
    return _query_por_slug(db, slug).first()
