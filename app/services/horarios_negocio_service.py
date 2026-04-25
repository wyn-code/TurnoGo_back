# app/services/horario_negocio_service.py

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.horarios_negocio import HorarioNegocio
from app.schemas.horarios_negocio_schema import HorarioNegocioCreate


def crear_horarios(
    db: Session,
    id_negocio: int,
    horarios: list[HorarioNegocioCreate]
):
    for h in horarios:
        nuevo = HorarioNegocio(
            id_negocio=id_negocio,
            dia_semana=h.dia_semana,
            hora_apertura=h.hora_apertura,
            hora_cierre=h.hora_cierre
        )
        db.add(nuevo)

    db.commit()
    return {"message": "Horarios guardados correctamente"}


def obtener_horarios_por_negocio(
    db: Session,
    id_negocio: int
):
    horarios = db.query(HorarioNegocio).filter(
        HorarioNegocio.id_negocio == id_negocio
    ).all()

    if not horarios:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron horarios para este negocio"
        )

    return horarios


def actualizar_horarios(
    db: Session,
    id_negocio: int,
    horarios: list[HorarioNegocioCreate]
):
    existentes = db.query(HorarioNegocio).filter(
        HorarioNegocio.id_negocio == id_negocio
    ).all()

    if not existentes:
        raise HTTPException(
            status_code=404,
            detail="No existen horarios para actualizar"
        )

    db.query(HorarioNegocio).filter(
        HorarioNegocio.id_negocio == id_negocio
    ).delete()

    for h in horarios:
        nuevo = HorarioNegocio(
            id_negocio=id_negocio,
            dia_semana=h.dia_semana,
            hora_apertura=h.hora_apertura,
            hora_cierre=h.hora_cierre
        )
        db.add(nuevo)

    db.commit()

    return {"message": "Horarios actualizados correctamente"}


def eliminar_horarios(
    db: Session,
    id_negocio: int
):
    horarios = db.query(HorarioNegocio).filter(
        HorarioNegocio.id_negocio == id_negocio
    ).all()

    if not horarios:
        raise HTTPException(
            status_code=404,
            detail="No existen horarios para eliminar"
        )

    db.query(HorarioNegocio).filter(
        HorarioNegocio.id_negocio == id_negocio
    ).delete()

    db.commit()

    return {"message": "Horarios eliminados correctamente"}