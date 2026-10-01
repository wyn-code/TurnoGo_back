"""Espacios reservables de un negocio (antes "canchas").

Rutas nuevas: GET /negocios/{id}/espacios, POST /espacios, PUT|DELETE
/espacios/{id}. Las rutas legadas `/canchas/...` (cancha_router.py) reutilizan
estos mismos handlers.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.espacio import Espacio
from app.models.negocio import Negocio
from app.models.usuario import Usuario
from app.schemas.espacio_schema import (
    EspacioBase,
    EspacioCreate,
    EspacioResponse,
    EspacioUpdate,
)


router = APIRouter(tags=["Espacios"])


def _obtener_negocio_autorizado(
    db: Session,
    id_negocio: int,
    current_user: Usuario,
) -> Negocio:
    negocio = db.query(Negocio).filter(
        Negocio.id_negocio == id_negocio
    ).first()

    if not negocio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negocio no encontrado",
        )

    if negocio.usuario_id != current_user.id_us and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permisos para modificar los espacios de este negocio",
        )

    return negocio


def _obtener_espacio_de_negocio(
    db: Session,
    id_espacio: int,
    current_user: Usuario,
) -> Espacio:
    espacio = db.query(Espacio).filter(Espacio.id_espacio == id_espacio).first()

    if not espacio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Espacio no encontrado",
        )

    _obtener_negocio_autorizado(db, espacio.id_negocio, current_user)

    return espacio


def _crear(db: Session, id_negocio: int, datos: EspacioBase, current_user: Usuario):
    _obtener_negocio_autorizado(db, id_negocio, current_user)

    nuevo = Espacio(
        nombre=datos.nombre.strip(),
        numero=datos.numero,
        descripcion=datos.descripcion,
        id_negocio=id_negocio,
    )
    db.add(nuevo)

    try:
        db.commit()
        db.refresh(nuevo)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el espacio",
        )

    return nuevo


# ── PÚBLICO: la página de reserva necesita el listado de espacios ──


@router.get("/negocios/{id_negocio}/espacios", response_model=list[EspacioResponse])
def listar_espacios(
    id_negocio: int,
    incluir_inactivas: bool = False,
    db: Session = Depends(get_db),
):
    query = db.query(Espacio).filter(Espacio.id_negocio == id_negocio)

    # La página de reserva sólo necesita los activos; el dashboard pide todos.
    if not incluir_inactivas:
        query = query.filter(Espacio.activo.is_(True))

    return query.order_by(Espacio.numero.asc().nulls_last(), Espacio.id_espacio.asc()).all()


@router.post(
    "/espacios",
    response_model=EspacioResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_espacio(
    datos: EspacioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return _crear(db, datos.id_negocio, datos, current_user)


def crear_espacio_en_negocio(
    id_negocio: int,
    datos: EspacioBase,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Variante con id_negocio en el path (ruta legada POST /canchas/negocio/{id})."""
    return _crear(db, id_negocio, datos, current_user)


@router.put("/espacios/{id_espacio}", response_model=EspacioResponse)
def actualizar_espacio(
    id_espacio: int,
    datos: EspacioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    espacio = _obtener_espacio_de_negocio(db, id_espacio, current_user)

    cambios = datos.model_dump(exclude_unset=True)
    if cambios.get("nombre") is not None:
        espacio.nombre = cambios["nombre"].strip()
    if "numero" in cambios:
        espacio.numero = cambios["numero"]
    if "descripcion" in cambios:
        espacio.descripcion = cambios["descripcion"]
    if cambios.get("activo") is not None:
        espacio.activo = cambios["activo"]

    db.commit()
    db.refresh(espacio)

    return espacio


@router.delete("/espacios/{id_espacio}")
def eliminar_espacio(
    id_espacio: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Baja lógica: los turnos históricos siguen apuntando al espacio."""
    espacio = _obtener_espacio_de_negocio(db, id_espacio, current_user)

    espacio.activo = False
    db.commit()

    return {"message": "Espacio eliminado"}
