from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Text,
    Integer,
)
from sqlalchemy.orm import relationship, synonym
from datetime import datetime
from app.db.base import Base
from app.models.estado_turno import EstadoTurno


class Turno(Base):
    """Turno de un negocio sobre UN recurso: un empleado o un espacio.

    La regla "no ambos" vive en el CHECK de DB (acá) y se valida antes en
    `turno_service.validar_recurso_unico`. Se admiten turnos sin recurso
    (negocios sin empleados) por compatibilidad.
    """

    __tablename__ = "turno"
    __table_args__ = (
        CheckConstraint(
            "id_empleado IS NULL OR id_espacio IS NULL",
            name="chk_turno_no_empleado_y_espacio",
        ),
    )

    id_turno = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_negocio = Column(
        Integer,
        ForeignKey(
            "negocio.id_negocio",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    id_servicio = Column(
        Integer,
        ForeignKey(
            "servicio.id_servicio",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    id_empleado = Column(
        Integer,
        ForeignKey(
            "empleado.id_empleado",
            ondelete="CASCADE",
        ),
    )
    # SET NULL (no CASCADE): borrar un espacio no debe borrar el historial.
    id_espacio = Column(
        Integer,
        ForeignKey(
            "espacio.id_espacio",
            ondelete="SET NULL",
            name="fk_turno_espacio",
        ),
        index=True,
    )
    id_cancha = synonym("id_espacio")  # alias legado
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=False)
    id_estado = Column(Integer, ForeignKey('estado_turno.id_estado'), nullable=False)
    fecha_hora_inicio = Column(DateTime, nullable=False)
    fecha_hora_fin = Column(DateTime)
    rechazado_motivo = Column(Text)
    recordatorio_enviado = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    negocio = relationship(
        "Negocio",
        back_populates="turnos",
    )
    cliente = relationship("Cliente", back_populates="turnos")
    empleado = relationship("Empleado", back_populates="turnos")
    espacio = relationship("Espacio", back_populates="turnos")
    cancha = synonym("espacio")  # alias legado
    servicio = relationship("Servicio", back_populates="turnos")
    estado = relationship("EstadoTurno")

    @property
    def recurso(self):
        """El recurso reservado: el espacio si hay, si no el empleado (o None)."""
        return self.espacio if self.id_espacio is not None else self.empleado
