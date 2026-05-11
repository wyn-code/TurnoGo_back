from pydantic import BaseModel, ConfigDict
from datetime import time

class HorarioNegocioCreate(BaseModel):
    dia_semana: int
    hora_apertura: time
    hora_cierre: time


class HorarioNegocioResponse(HorarioNegocioCreate):
    id_horarios_negocio: int
    id_negocio: int

    model_config = ConfigDict(from_attributes=True)