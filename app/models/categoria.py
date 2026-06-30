import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, Integer, String
from app.db.base import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    icono = Column(String(500), nullable=True)
    descripcion = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

    negocios = relationship("Negocio", back_populates="categoria")
