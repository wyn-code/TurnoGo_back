import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from app.db.base import Base


class Categoria(Base):
    """Categoría de negocio. Jerárquica: `parent_id` nulo = categoría raíz."""

    __tablename__ = "categorias"

    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    icono = Column(String(500), nullable=True)
    descripcion = Column(String(255), nullable=True)
    parent_id = Column(
        Integer,
        ForeignKey("categorias.id_categoria", name="categorias_parent_id_fkey"),
        nullable=True,
        index=True,
    )
    created_at = Column(DateTime, default=datetime.datetime.now)

    negocios = relationship("Negocio", back_populates="categoria")
    parent = relationship(
        "Categoria",
        remote_side=[id_categoria],
        back_populates="children",
    )
    children = relationship(
        "Categoria",
        back_populates="parent",
        order_by="Categoria.nombre",
    )
