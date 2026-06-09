from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime


class Negocio(Base):
    __tablename__ = "negocio"

    id_negocio = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id_us"), nullable=False, unique=True)
    nombre = Column(String(150), nullable=False)
    wsp = Column(String(20), nullable=False)
    telefono = Column(String(20), nullable=True)
    direccion = Column(String(200), nullable=False)
    ciudad = Column(String(100), nullable=False)
    id_localidad = Column(Integer, ForeignKey("localidad.id_localidad"), nullable=True)
    id_provincia = Column(Integer, ForeignKey("provincias.id_provincia"), nullable=True)
    ig_url = Column(String(200), nullable=True)
    slug = Column(String(150), unique=True, nullable=False, index=True)
    logo = Column(String(255), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    creado_at = Column(DateTime, default=datetime.now, nullable=False)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"), nullable=False)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)

    turnos = relationship("Turno", back_populates="negocio")
    servicios = relationship("Servicio", back_populates="negocio", cascade="all, delete-orphan")
    empleados = relationship("Empleado", back_populates="negocio", cascade="all, delete-orphan")
    usuario = relationship("Usuario", back_populates="negocio")
    categoria = relationship("Categoria", back_populates="negocios")
    horarios = relationship("HorarioNegocio", back_populates="negocio", cascade="all, delete-orphan")
