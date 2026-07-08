from sqlalchemy import Boolean, Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from app.db.base import Base


class Plan(Base):
    __tablename__ = "planes"

    id_plan = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    precio = Column(Numeric, nullable=False)
    duracion_dias = Column(Integer, nullable=False)
    descripcion = Column(String(500), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)

    funciones = relationship("PlanFeature", back_populates="plan", cascade="all, delete-orphan")
    suscripciones = relationship("Suscripcion", back_populates="plan")

    @property
    def feature_keys(self) -> list[str]:
        return [pf.feature_key for pf in self.funciones]
