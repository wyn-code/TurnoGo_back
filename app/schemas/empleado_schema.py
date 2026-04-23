from pydantic import BaseModel, ConfigDict


class EmpleadoBase(BaseModel):
    nombre: str
    apellido: str
    telefono: str
    activo: bool = True  # 👈 le damos default por si no viene


class EmpleadoCreate(EmpleadoBase):
    pass


class EmpleadoResponse(EmpleadoBase):
    id_empleado: int
    model_config = ConfigDict(from_attributes=True)