from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.appointment_schema import (
    TurnoCrear,
    TurnoActualizar,
    TurnoResponse,
)
from app.services.turno_service import (
    listar_turnos,
    obtener_turno_por_id,
    crear_turno,
    actualizar_turno,
    borrar_turno,
)

router = APIRouter(prefix="/turnos", tags=["Turnos"])


@router.get("/", response_model=list[TurnoResponse])
def listar(db: Session = Depends(get_db)):
    return listar_turnos(db)


@router.get("/{turno_id}", response_model=TurnoResponse)
def obtener(turno_id: int, db: Session = Depends(get_db)):
    turno = obtener_turno_por_id(db, turno_id)
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    return turno


@router.post("/", response_model=TurnoResponse, status_code=201)
def crear(turno: TurnoCrear, db: Session = Depends(get_db)):
    return crear_turno(db, turno)


@router.put("/{turno_id}", response_model=TurnoResponse)
def actualizar(turno_id: int, datos: TurnoActualizar, db: Session = Depends(get_db)):
    return actualizar_turno(db, turno_id, datos)


@router.delete("/{turno_id}")
def borrar(turno_id: int, db: Session = Depends(get_db)):
    borrar_turno(db, turno_id)
    return {"mensaje": "Turno eliminado"}