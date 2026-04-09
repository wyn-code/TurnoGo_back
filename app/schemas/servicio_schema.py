from typing import Optional

from pydantic import BaseModel, ConfigDict


class ServicioBase(BaseModel):
    nombre_servicio: str
    precio: float
    requiere_aprobacion: bool
    duracion_min: int
    duracion_max: Optional[int] = None
    activo: bool = True


class ServicioCreate(ServicioBase):
    pass


class ServicioResponse(ServicioBase):
    id_servicio: int
    model_config = ConfigDict(from_attributes=True)
