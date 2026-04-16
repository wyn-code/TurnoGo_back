from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.empleado import Empleado
from app.models.negocio import Negocio
from app.schemas.empleado_schema import EmpleadoCreate


def _query_empleado_por_id(db: Session, empleado_id: int):
    return db.query(Empleado).filter(Empleado.id_empleado == empleado_id)


def ver_empleados(db: Session):
    return db.query(Empleado).all()


def ver_empleado_por_id(db: Session, empleado_id: int):
    return _query_empleado_por_id(db, empleado_id).first()


def validar_negocio_existe(db: Session, id_negocio: int):
    negocio = db.query(Negocio).filter(Negocio.id_negocio == id_negocio).first()
    if not negocio:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return negocio


def crear_empleado(db: Session, empleado: EmpleadoCreate):
    validar_negocio_existe(db, empleado.id_negocio)

    nuevo_empleado = Empleado(
        id_negocio=empleado.id_negocio,
        nombre=empleado.nombre.strip(),
        apellido=empleado.apellido.strip(),
        telefono=empleado.telefono.strip(),
        activo=empleado.activo,
    )
    db.add(nuevo_empleado)
    db.commit()
    db.refresh(nuevo_empleado)
    return nuevo_empleado