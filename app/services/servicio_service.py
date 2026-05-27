from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.servicio import Servicio

from app.schemas.servicio_schema import (
    ServicioCreate,
    ServicioUpdate
)


# =========================
# LISTAR SERVICIOS
# =========================

def listar_servicios(
    db: Session,
    id_negocio: int | None = None
):
    query = db.query(Servicio)

    if id_negocio:
        query = query.filter(
            Servicio.id_negocio == id_negocio
        )

    return query.all()


# =========================
# CREAR SERVICIO
# =========================

def crear_servicio(
    db: Session,
    data: ServicioCreate
):
    nuevo_servicio = Servicio(
        **data.model_dump()
    )

    db.add(nuevo_servicio)

    db.commit()

    db.refresh(nuevo_servicio)

    return nuevo_servicio


# =========================
# ACTUALIZAR SERVICIO
# =========================

def actualizar_servicio(
    db: Session,
    id_servicio: int,
    data: ServicioUpdate
):
    servicio = (
        db.query(Servicio)
        .filter(
            Servicio.id_servicio == id_servicio
        )
        .first()
    )

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(servicio, key, value)

    db.commit()

    db.refresh(servicio)

    return servicio


# =========================
# ELIMINAR SERVICIO
# DELETE LÓGICO
# =========================

def eliminar_servicio(
    db: Session,
    id_servicio: int
):
    servicio = (
        db.query(Servicio)
        .filter(
            Servicio.id_servicio == id_servicio
        )
        .first()
    )

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    servicio.activo = False

    db.commit()

    db.refresh(servicio)

    return servicio


# =========================
# TOGGLE SERVICIO
# =========================

def toggle_servicio(
    db: Session,
    id_servicio: int
):
    servicio = (
        db.query(Servicio)
        .filter(
            Servicio.id_servicio == id_servicio
        )
        .first()
    )

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    servicio.activo = not servicio.activo

    db.commit()

    db.refresh(servicio)

    return servicio
