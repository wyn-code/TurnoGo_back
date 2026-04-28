from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator, ConfigDict


def _validar_rango_horario(
    fecha_hora_inicio: Optional[datetime],
    fecha_hora_fin: Optional[datetime],
) -> None:
    if (
        fecha_hora_inicio is not None
        and fecha_hora_fin is not None
        and fecha_hora_fin <= fecha_hora_inicio
    ):
        raise ValueError("fecha_hora_fin debe ser mayor que fecha_hora_inicio")


class TurnoCrear(BaseModel):
    id_negocio: int
    id_cliente: int
    id_servicio: int
    fecha_hora_inicio: datetime
    id_empleado: Optional[int] = None


class TurnoActualizar(BaseModel):
    id_negocio: Optional[int] = None
    id_cliente: Optional[int] = None
    id_servicio: Optional[int] = None
    id_estado: Optional[int] = None
    id_empleado: Optional[int] = None
    fecha_hora_inicio: Optional[datetime] = None
    fecha_hora_fin: Optional[datetime] = None
    rechazado_motivo: Optional[str] = None

    @model_validator(mode="after")
    def validar_rango_horario(self):
        _validar_rango_horario(self.fecha_hora_inicio, self.fecha_hora_fin)
        return self

class ClienteSimple(BaseModel):
    id_cliente: int
    nombre: str

    model_config = ConfigDict(from_attributes=True)


class EmpleadoSimple(BaseModel):
    id_empleado: int
    nombre: str

    model_config = ConfigDict(from_attributes=True)

class ServicioSimple(BaseModel):
    id_servicio: int
    nombre_servicio: str

    model_config = ConfigDict(from_attributes=True)


class EstadoSimple(BaseModel):
    id_estado: int
    nombre_estado: str

    model_config = ConfigDict(from_attributes=True)

class TurnoResponse(BaseModel):
    id_turno: int
    id_negocio: int

    fecha_hora_inicio: datetime
    fecha_hora_fin: Optional[datetime] = None
    rechazado_motivo: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    cliente: ClienteSimple
    empleado: Optional[EmpleadoSimple] = None
    servicio: ServicioSimple
    estado: EstadoSimple

    model_config = ConfigDict(from_attributes=True)
