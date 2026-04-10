from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.servicio import Servicio
from app.schemas.servicio_schema import ServicioCreate


def listar_servicios(db: Session):
    return db.query(Servicio).all()


def crear_servicio(db: Session, data: ServicioCreate):
    nuevo_servicio = Servicio(**data.model_dump())
    db.add(nuevo_servicio)
    db.commit()
    db.refresh(nuevo_servicio)
    return nuevo_servicio


def eliminar_servicio(db: Session, id_servicio: int):
    servicio = db.query(Servicio).filter(Servicio.id_servicio == id_servicio).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    db.delete(servicio)
    db.commit()