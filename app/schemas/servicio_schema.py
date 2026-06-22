from typing import Optional
from pydantic import BaseModel, ConfigDict


class ServicioBase(BaseModel):
    nombre_servicio: str
    precio: float
    requiere_aprobacion: bool = False 
    duracion_min: int
    duracion_max: int
    activo: bool = True

class ServicioUpdate(BaseModel):
    nombre_servicio: Optional[str] = None
    precio: Optional[float] = None
    requiere_aprobacion: Optional[bool] = None
    duracion_min: Optional[int] = None
    duracion_max: Optional[int] = None
    activo: Optional[bool] = None


class ServicioCreate(ServicioBase):
    id_negocio: int # Necesitamos saber a qué negocio pertenece el servicio


class ServicioCreateNested(ServicioBase):
    pass


class ServicioResponse(ServicioBase):
    id_servicio: int
    id_negocio: int

    model_config = ConfigDict(from_attributes=True)
