from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Negocio(Base):
    __tablename__ = "negocios"

    id_negocio = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    rubro = Column(String(100), nullable=False)
    wsp = Column(String(20), nullable=False)
    telefono = Column(String(20), nullable=True)
    direccion = Column(String(200), nullable=False)
    ciudad = Column(String(100), nullable=False)

    id_localidad = Column(
        Integer,
        ForeignKey("localidades.id_localidad"),
        nullable=True
    )
    id_provincia = Column(
        Integer,
        ForeignKey("provincias.id_provincia"),
        nullable=True
    )

    ig_url = Column(String(200), nullable=True)
    slug = Column(String(150), unique=True, nullable=False, index=True)
    logo = Column(String(255), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    creado_at = Column(DateTime, default=datetime.now, nullable=False)

    turnos = relationship("Turno", back_populates="negocio")
