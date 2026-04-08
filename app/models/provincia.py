from sqlalchemy import Column, Integer, String
from app.db.base import Base


class Provincia(Base):
    __tablename__ = "provincias"
    id_provincia = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
