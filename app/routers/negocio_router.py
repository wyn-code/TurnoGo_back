from fastapi import Request
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.categoria import Categoria
from app.core.dependencies import get_current_user, get_db
from app.models.usuario import Usuario
from app.schemas.negocio_schema import (
    NegocioCreate,
    NegocioResponse,
    NegocioCompleteCreate,
    NegocioCompleteResponse,
    NegocioAdminResponse,
    NegocioUpdate,
)
from app.services.negocio_service import (
    listar_negocios,
    listar_negocios_admin,
    obtener_negocio_por_id,
    obtener_negocio_publico_por_id,
    obtener_negocio_por_slug,
    crear_negocio,
    crear_negocio_completo,
)

router = APIRouter(prefix="/negocios", tags=["Negocios"])


@router.get("/", response_model=list[NegocioResponse])
def ver_negocios(db: Session = Depends(get_db)):
    return listar_negocios(db)


@router.get(
    "/admin",
    response_model=list[NegocioAdminResponse]
)
def ver_negocios_admin(
    db: Session = Depends(get_db)
):
    return listar_negocios_admin(db)


@router.get("/slug/{slug}", response_model=NegocioResponse)
def ver_negocio_por_slug(slug: str, db: Session = Depends(get_db)):
    negocio = obtener_negocio_por_slug(db, slug)
    if not negocio:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return negocio


@router.get("/{negocio_id}")
def ver_negocio_por_id(
    negocio_id: int,
    db: Session = Depends(get_db)
):
    negocio = obtener_negocio_publico_por_id(
        db,
        negocio_id
    )

    return negocio


@router.post("/", response_model=NegocioResponse, status_code=status.HTTP_201_CREATED)
def post_negocio(data: NegocioCreate, db: Session = Depends(get_db)):
    print(data.model_dump())

    if data.id_categoria is None:
        raise HTTPException(
            status_code=400, detail="id_categoria es obligatorio")

    return crear_negocio(db, data)


@router.post("/complete", response_model=NegocioCompleteResponse, status_code=status.HTTP_201_CREATED)
def post_negocio_completo(data: NegocioCompleteCreate, db: Session = Depends(get_db)):
    if data.id_categoria is None:
        raise HTTPException(status_code=400, detail="id_categoria es obligatorio")

    return crear_negocio_completo(db, data)

@router.put("/{negocio_id}", response_model=NegocioResponse)
def update_negocio(
    negocio_id: int,
    data: NegocioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    negocio = obtener_negocio_por_id(
        db,
        negocio_id
    )

    es_admin = (
        current_user.role == "admin"
    )

    es_duenio = (
        negocio.usuario_id
        == current_user.id_us
    )

    if not es_admin and not es_duenio:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para editar este negocio"
        )

    # ✅ Validar categoría SOLO si viene
    if data.id_categoria is not None:

        categoria = db.query(Categoria).filter(
            Categoria.id_categoria == data.id_categoria
        ).first()

        if not categoria:
            raise HTTPException(
                status_code=400,
                detail="Categoría no válida"
            )

    # ✅ Actualizar solo campos enviados
    for key, value in data.model_dump(
        exclude_unset=True
    ).items():
        setattr(negocio, key, value)

    db.commit()
    db.refresh(negocio)

    return negocio


@router.delete("/{negocio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_negocio(
    negocio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo los administradores pueden eliminar negocios"
        )

    negocio = obtener_negocio_por_id(db, negocio_id)

    if not negocio:
        raise HTTPException(
            status_code=404,
            detail="Negocio no encontrado"
        )

    db.delete(negocio)
    db.commit()

    return None
