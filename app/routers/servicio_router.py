from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.servicio_schema import ServicioCreate, ServicioResponse
from app.services.servicio_service import (
    crear_servicio as crear_servicio_service,
    eliminar_servicio as eliminar_servicio_service,
    listar_servicios as listar_servicios_service,
)

router = APIRouter(prefix="/servicios", tags=["Servicios"])


@router.get("/", response_model=list[ServicioResponse])
def listar_servicios(db: Session = Depends(get_db)):
    return listar_servicios_service(db)


@router.post("/", response_model=ServicioResponse, status_code=status.HTTP_201_CREATED)
def crear_servicio(data: ServicioCreate, db: Session = Depends(get_db)):
    return crear_servicio_service(db, data)


@router.delete("/{id_servicio}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_servicio(id_servicio: int, db: Session = Depends(get_db)):
    eliminar_servicio_service(db, id_servicio)