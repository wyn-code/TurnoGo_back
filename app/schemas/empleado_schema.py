from pydantic import BaseModel, ConfigDict

class EmpleadoBase(BaseModel):
    nombre: str
    apellido: str
    telefono: str
    activo: bool

class EmpleadoCreate(EmpleadoBase):
    id_negocio: int


class EmpleadoResponse(EmpleadoBase):
    id_empleado: int
    id_negocio: int
    model_config = ConfigDict(from_attributes=True)
