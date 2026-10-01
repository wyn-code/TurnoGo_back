from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship, synonym
from datetime import datetime
from app.db.base import Base


class Espacio(Base):
    """Recurso reservable de un negocio (cancha, salón, box…).

    Un negocio puede tener varios espacios. Es la alternativa a `Empleado`
    como recurso de un turno (ver `Turno.recurso`).

    Antes se llamaba `Cancha`; `id_cancha` se mantiene como alias para no
    romper código ni clientes existentes.
    """

    __tablename__ = "espacio"
    __table_args__ = (Index("idx_espacio_negocio", "id_negocio"),)

    id_espacio = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    numero = Column(Integer, nullable=True)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    id_negocio = Column(
        Integer,
        ForeignKey(
            "negocio.id_negocio",
            ondelete="CASCADE",
            name="fk_espacio_negocio",
        ),
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    id_cancha = synonym("id_espacio")  # alias legado

    negocio = relationship(
        "Negocio",
        back_populates="espacios",
    )
    turnos = relationship(
        "Turno",
        back_populates="espacio",
        passive_deletes=True,
    )
