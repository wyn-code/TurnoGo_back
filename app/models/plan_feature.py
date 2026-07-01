from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base


class PlanFeature(Base):
    __tablename__ = "plan_features"

    id_feature = Column(Integer, primary_key=True, index=True)
    id_plan = Column(Integer, ForeignKey("planes.id_plan"), nullable=False)
    feature_key = Column(String(100), nullable=False)

    plan = relationship("Plan", back_populates="funciones")
