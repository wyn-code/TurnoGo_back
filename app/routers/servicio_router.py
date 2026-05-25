from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user
)

from app.db.session import get_db

from app.models.usuario import Usuario
from app.models.negocio import Negocio
from app.models.servicio import Servicio

from app.schemas.servicio_schema import (
    ServicioCreate,
    ServicioResponse,
    ServicioUpdate
)

from app.services.servicio_service import (
    crear_servicio as crear_servicio_service,
    eliminar_servicio as eliminar_servicio_service,
    listar_servicios as listar_servicios_service,
    actualizar_servicio as actualizar_servicio_service,
    toggle_servicio as toggle_servicio_service,
)

router = APIRouter(
    prefix="/servicios",
    tags=["Servicios"]
)


# =========================
# LISTAR SERVICIOS
# =========================

@router.get(
    "/",
    response_model=list[ServicioResponse]
)
def listar_servicios(
    id_negocio: int | None = None,
    db: Session = Depends(get_db)
):
    return listar_servicios_service(
        db,
        id_negocio
    )


# =========================
# CREAR SERVICIO
# =========================

@router.post(
    "/",
    response_model=ServicioResponse
)
def crear_servicio(
    data: ServicioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        get_current_user
    )
):
    negocio = (
        db.query(Negocio)
        .filter(
            Negocio.id_negocio
            == data.id_negocio
        )
        .first()
    )

    if not negocio:
        raise HTTPException(
            status_code=404,
            detail="Negocio no encontrado"
        )

    if (
        negocio.usuario_id
        != current_user.id_us
    ):
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para agregar servicios a este negocio"
        )

    return crear_servicio_service(
        db,
        data
    )


# =========================
# ACTUALIZAR SERVICIO
# =========================

@router.put(
    "/{id_servicio}",
    response_model=ServicioResponse
)
def actualizar_servicio(
    id_servicio: int,
    data: ServicioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        get_current_user
    )
):
    servicio = (
        db.query(Servicio)
        .filter(
            Servicio.id_servicio
            == id_servicio
        )
        .first()
    )

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    if (
        servicio.negocio.usuario_id
        != current_user.id_us
    ):
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos"
        )

    return actualizar_servicio_service(
        db,
        id_servicio,
        data
    )


# =========================
# TOGGLE SERVICIO
# =========================

@router.patch(
    "/{id_servicio}",
    response_model=ServicioResponse
)
def toggle_servicio(
    id_servicio: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        get_current_user
    )
):
    servicio = (
        db.query(Servicio)
        .filter(
            Servicio.id_servicio
            == id_servicio
        )
        .first()
    )

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    if (
        servicio.negocio.usuario_id
        != current_user.id_us
    ):
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos"
        )

    return toggle_servicio_service(
        db,
        id_servicio
    )


# =========================
# ELIMINAR SERVICIO
# DELETE LÓGICO
# =========================

@router.delete(
    "/{id_servicio}",
    response_model=ServicioResponse
)
def eliminar_servicio(
    id_servicio: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        get_current_user
    )
):
    servicio = (
        db.query(Servicio)
        .filter(
            Servicio.id_servicio
            == id_servicio
        )
        .first()
    )

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado"
        )

    if (
        servicio.negocio.usuario_id
        != current_user.id_us
    ):
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos"
        )

    return eliminar_servicio_service(
        db,
        id_servicio
    )