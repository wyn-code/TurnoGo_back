from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class NegocioBase(BaseModel):
    nombre: str
    rubro: str
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


class ServicioNestedCreate(BaseModel):
    nombre_servicio: str
    precio: float
    requiere_aprobacion: bool = False
    duracion_min: int
    duracion_max: int
    activo: bool = True


class EmpleadoNestedCreate(BaseModel):
    nombre: str
    apellido: str
    telefono: str
    activo: bool = True


class NegocioCompleteCreate(NegocioCreate):
    servicios: List[ServicioNestedCreate] = []
    empleados: List[EmpleadoNestedCreate] = []


class ServicioNestedResponse(ServicioNestedCreate):
    id_servicio: int
    id_negocio: int

    model_config = ConfigDict(from_attributes=True)


class EmpleadoNestedResponse(EmpleadoNestedCreate):
    id_empleado: int
    id_negocio: int

    model_config = ConfigDict(from_attributes=True)


class NegocioResponse(NegocioBase):
    id_negocio: int
    creado_at: datetime
    model_config = ConfigDict(from_attributes=True)
    slug: str


class NegocioCompleteResponse(NegocioResponse):
    servicios: List[ServicioNestedResponse] = []
    empleados: List[EmpleadoNestedResponse] = []

    model_config = ConfigDict(from_attributes=True)
