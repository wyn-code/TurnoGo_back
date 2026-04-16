from fastapi import APIRouter, Depends, HTTPException
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
    obtener_negocio_por_slug,
    crear_negocio,
    crear_negocio_completo,
)

router = APIRouter(prefix="/negocios", tags=["Negocios"])


@router.get("/", response_model=list[NegocioResponse])
def ver_negocios(db: Session = Depends(get_db)):
    return listar_negocios(db)


@router.get("/slug/{slug}", response_model=NegocioResponse)
def ver_negocio_por_slug(slug: str, db: Session = Depends(get_db)):
    negocio = obtener_negocio_por_slug(db, slug)
    if not negocio:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return negocio


@router.get("/{negocio_id}", response_model=NegocioResponse)
def ver_negocio_por_id(negocio_id: int, db: Session = Depends(get_db)):
    return obtener_negocio_por_id(db, negocio_id)


@router.post("/", response_model=NegocioResponse, status_code=201)
def post_negocio(data: NegocioCreate, db: Session = Depends(get_db)):
    return crear_negocio(db, data)


@router.post("/complete", response_model=NegocioCompleteResponse, status_code=201)
def post_negocio_completo(data: NegocioCompleteCreate, db: Session = Depends(get_db)):
    return crear_negocio_completo(db, data)


@router.put("/{negocio_id}", response_model=NegocioResponse)
def update_negocio(negocio_id: int, data: NegocioCreate, db: Session = Depends(get_db)):
    negocio = obtener_negocio_por_id(db, negocio_id)

    for key, value in data.model_dump().items():
        setattr(negocio, key, value)

    db.commit()
    db.refresh(negocio)
    return negocio


@router.delete("/{negocio_id}", status_code=204)
def delete_negocio(negocio_id: int, db: Session = Depends(get_db)):
    negocio = obtener_negocio_por_id(db, negocio_id)
    db.delete(negocio)
    db.commit()