from sqlalchemy import Column, DateTime, ForeignKey, Text, SmallInteger, BigInteger, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Turno(Base):
    __tablename__ = "turno"

    id_turno = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_negocio = Column(Integer, ForeignKey("negocio.id_negocio"), nullable=False)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=False)
    id_servicio = Column(Integer, ForeignKey("servicio.id_servicio"), nullable=False)
    id_estado = Column(Integer, nullable=False), ForeignKey("estado_turno.id_estado")
    id_empleado = Column(Integer, ForeignKey("empleado.id_empleado"))
    fecha_hora_inicio = Column(DateTime, nullable=False)
    fecha_hora_fin = Column(DateTime)
    id_admin_aprobador = Column(Integer, ForeignKey("usuarios.id_us"))
    aprobado_at = Column(DateTime)
    rechazado_motivo = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    negocio = relationship("Negocio", back_populates="turnos")
    cliente = relationship("Cliente", back_populates="turnos")
    empleado = relationship("Empleado", back_populates="turnos")
    servicio = relationship("Servicio", back_populates="turnos")
    admin_aprobador = relationship("Usuario")