from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, Integer, String

from app.db.base import Base


class Empleado(Base):
    __tablename__ = "empleado"

    id_empleado = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(30), nullable=False)
    apellido = Column(String(30), nullable=False)
    telefono = Column(String(30), unique=True, nullable=False)
    activo = Column(Boolean, nullable=False)

    turnos = relationship("Turno", back_populates="empleado")