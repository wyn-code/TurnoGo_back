from typing import Optional
from pydantic import BaseModel, ConfigDict



class EmpleadoBase(BaseModel):
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    activo: bool = True


class EmpleadoCreate(EmpleadoBase):
    pass  # ❌ NO id_negocio


class EmpleadoResponse(EmpleadoBase):
    id_empleado: int
    id_negocio: int

    model_config = ConfigDict(from_attributes=True)