from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.servicio_schema import (
    ServicioCreate,
    ServicioResponse
)

from app.schemas.empleado_schema import (
    EmpleadoCreate,
    EmpleadoResponse
)

from app.schemas.categoria_schema import (
    CategoriaResponse
)


class NegocioBase(BaseModel):
    nombre: str
    id_categoria: int
    wsp: str
    telefono: Optional[str] = None
    direccion: str
    ciudad: str
    id_localidad: Optional[int] = None
    id_provincia: Optional[int] = None
    ig_url: Optional[str] = None
    logo: Optional[str] = None
    activo: bool = True


class NegocioCreate(NegocioBase):
    usuario_id: int
    id_categoria: int


class NegocioResponse(NegocioBase):
    id_negocio: int
    creado_at: datetime
    usuario_id: Optional[int] = None
    slug: Optional[str] = None
    categoria: Optional[CategoriaResponse] = None

    model_config = ConfigDict(
        from_attributes=True
    )


class NegocioCompleteCreate(
    NegocioCreate
):
    servicios: List[ServicioCreate] = (
        Field(default_factory=list)
    )

    empleados: List[EmpleadoCreate] = (
        Field(default_factory=list)
    )


class NegocioCompleteResponse(
    NegocioResponse
):
    servicios: List[ServicioResponse] = (
        Field(default_factory=list)
    )

    empleados: List[EmpleadoResponse] = (
        Field(default_factory=list)
    )


# =========================
# ADMIN RESPONSE
# =========================

class DuenioResponse(BaseModel):
    nombre: str
    email: str


class NegocioAdminResponse(BaseModel):
    id_negocio: int
    nombre: str
    categoria: str
    slug: str
    activo: bool
    duenio: DuenioResponse

    model_config = ConfigDict(
        from_attributes=True
    )