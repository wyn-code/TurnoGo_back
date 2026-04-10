from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.negocio_schema import (
    NegocioCreate,
    NegocioResponse,
    NegocioCompleteCreate,
    NegocioCompleteResponse,
)
from app.services.negocio_service import (
    listar_negocios,
    obtener_negocio_por_id,
    crear_negocio,
    crear_negocio_completo,
)

router = APIRouter(prefix="/negocios", tags=["Negocios"])


@router.get("/", response_model=list[NegocioResponse])
def ver_negocios(db: Session = Depends(get_db)):
    return listar_negocios(db)


@router.get("/{negocio_id}", response_model=NegocioResponse)
def ver_negocio_por_id(negocio_id: int, db: Session = Depends(get_db)):
    return obtener_negocio_por_id(db, negocio_id)


@router.post("/", response_model=NegocioResponse, status_code=201)
def post_negocio(data: NegocioCreate, db: Session = Depends(get_db)):
    return crear_negocio(db, data)


@router.post("/complete", response_model=NegocioCompleteResponse, status_code=201)
def post_negocio_completo(data: NegocioCompleteCreate, db: Session = Depends(get_db)):
    return crear_negocio_completo(db, data)