from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.schemas.negocio_schema import (
    NegocioCreate,
    NegocioResponse,
)
from app.services import negocio_service


router = APIRouter(prefix="/negocios", tags=["Negocios"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=NegocioResponse)
def crear_negocio(negocio: NegocioCreate, db: Session = Depends(get_db)):
    try:
        return negocio_service.crear_negocio(db, negocio)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[NegocioResponse])
def listar_negocios(db: Session = Depends(get_db)):
    return negocio_service.obtener_negocios(db)


@router.get("/id/{id_negocio}", response_model=NegocioResponse)
def traer_negocio_por_id(id_negocio: int, db: Session = Depends(get_db)):
    negocio = negocio_service.obtener_negocio_por_id(db, id_negocio)

    if not negocio:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")

    return negocio


@router.get("/slug/{slug}", response_model=NegocioResponse)
def traer_negocio_por_slug(slug: str, db: Session = Depends(get_db)):
    negocio = negocio_service.obtener_negocio_por_slug(db, slug)

    if not negocio:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")

    return negocio
