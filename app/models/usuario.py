from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from sqlalchemy.orm import relationship
from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_us = Column(Integer, primary_key=True, index=True)

    usuario_us = Column(String(50), nullable=False, unique=True)
    email_us = Column(String(100), nullable=False, unique=True, index=True)

    contrasena_us = Column(String(255), nullable=False)

    role = Column(String(20), default="duenio")

    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # RECUPERAR PASSWORD
    reset_token = Column(String(255), nullable=True)
    reset_token_expiration = Column(DateTime, nullable=True)

    negocio = relationship(
        "Negocio",
        back_populates="usuario",
        uselist=False,
    )

    email_verified = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    verification_token = Column(
        String(255),
        nullable=True,
    )

    verification_token_expiration = Column(
        DateTime,
        nullable=True,
    )