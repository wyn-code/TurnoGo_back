from sqlalchemy import Column, SmallInteger, String
from app.db.base import Base


class EstadoTurno(Base):
    __tablename__ = "estado_turno"  

    id_estado = Column(SmallInteger, primary_key=True, index=True)
    nombre_estado = Column(String(100), nullable=False)