"""Rutas legadas `/canchas/...`: alias deprecados de los endpoints de espacios.

Se mantienen para no romper clientes existentes; reutilizan los handlers de
espacio_router.py.
"""

from fastapi import APIRouter, status

from app.routers import espacio_router as er
from app.schemas.espacio_schema import EspacioResponse


router = APIRouter(prefix="/canchas", tags=["Canchas (deprecado)"])

router.add_api_route(
    "/negocio/{id_negocio}",
    er.listar_espacios,
    methods=["GET"],
    response_model=list[EspacioResponse],
    deprecated=True,
)
router.add_api_route(
    "/negocio/{id_negocio}",
    er.crear_espacio_en_negocio,
    methods=["POST"],
    response_model=EspacioResponse,
    status_code=status.HTTP_201_CREATED,
    deprecated=True,
)
router.add_api_route(
    "/{id_espacio}",
    er.actualizar_espacio,
    methods=["PUT"],
    response_model=EspacioResponse,
    deprecated=True,
)
router.add_api_route(
    "/{id_espacio}",
    er.eliminar_espacio,
    methods=["DELETE"],
    deprecated=True,
)
