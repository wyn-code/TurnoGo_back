from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.models.suscripcion import Suscripcion
from app.models.plan_feature import PlanFeature
from app.models.plan import Plan


def negocio_tiene_funcion(id_negocio: int, feature_key: str, db: Session) -> bool:
    """
    Devuelve True si el negocio tiene una suscripción activa (y no vencida)
    a un plan que incluya la feature_key indicada.
    """
    resultado = (
        db.query(Suscripcion)
        .join(Plan, Suscripcion.id_plan == Plan.id_plan)
        .join(PlanFeature, PlanFeature.id_plan == Plan.id_plan)
        .filter(
            Suscripcion.id_negocio == id_negocio,
            Suscripcion.estado == "activa",
            Suscripcion.fecha_fin >= datetime.now(),
            PlanFeature.feature_key == feature_key,
        )
        .first()
    )
    return resultado is not None


def obtener_funciones_negocio(id_negocio: int, db: Session) -> list[str]:
    """
    Devuelve la lista completa de feature_key habilitadas para el negocio,
    según su suscripción activa.
    """
    resultados = (
        db.query(PlanFeature.feature_key)
        .join(Plan, PlanFeature.id_plan == Plan.id_plan)
        .join(Suscripcion, Suscripcion.id_plan == Plan.id_plan)
        .filter(
            Suscripcion.id_negocio == id_negocio,
            Suscripcion.estado == "activa",
            Suscripcion.fecha_fin >= datetime.now(),
        )
        .all()
    )
    return [r.feature_key for r in resultados]


def obtener_suscripcion_activa(id_negocio: int, db: Session) -> Suscripcion | None:
    """
    Devuelve la suscripción activa del negocio (con su plan cargado), o None
    si no tiene ninguna (caso Free / sin suscripción).
    """
    return (
        db.query(Suscripcion)
        .join(Plan, Suscripcion.id_plan == Plan.id_plan)
        .filter(
            Suscripcion.id_negocio == id_negocio,
            Suscripcion.estado == "activa",
            Suscripcion.fecha_fin >= datetime.now(),
        )
        .first()
    )