from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base


class Localidad(Base):
    __tablename__ = "localidades"

    id_localidad = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    id_provincia = Column(
        Integer,
        ForeignKey("provincia.id_provincia"),
        nullable=True,
    )
