from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Cliente(Base):
    __tablename__ = "cliente"
    id_cliente = Column(Integer, primary_key=True, index=True, autoincrement=True)
    telefono = Column(String(30), nullable=False, unique=True)
    nombre = Column(String(30), nullable=False)
    apellido = Column(String(30), nullable=False)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    turnos = relationship("Turno", back_populates="cliente")
