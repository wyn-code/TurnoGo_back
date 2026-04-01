from pydantic import BaseModel
from typing import Optional

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

    class Config:
        from_attributes = True  # antes orm_mode = True