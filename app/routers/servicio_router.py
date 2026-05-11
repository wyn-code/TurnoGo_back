from fastapi import APIRouter, Depends, status, HTTPException # <-- Agrega HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.models.usuario import Usuario
from app.models.negocio import Negocio
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


@router.post("/") 
def crear_servicio(
    data: ServicioCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user) 
    ):
    negocio = db.query(Negocio).filter(Negocio.id_negocio == data.id_negocio).first()

    if not negocio:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
        
    if negocio.usuario_id != current_user.id_us:
        raise HTTPException(status_code=403, detail="No tienes permisos para agregar servicios a este negocio")
        
    return crear_servicio_service(db, data)


@router.delete("/{id_servicio}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_servicio(id_servicio: int, db: Session = Depends(get_db)):
    eliminar_servicio_service(db, id_servicio)