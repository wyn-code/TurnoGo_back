from app.db.base import SessionLocal
from app.models.plan import Plan
from app.models.plan_feature import PlanFeature
from sqlalchemy.exc import SQLAlchemyError

PLANES = [
    {
        "nombre": "Free",
        "precio": 0,
        "duracion_dias": 0,
        "descripcion": "Plan gratuito con funcionalidades básicas. Ideal para probar la plataforma.",
        "features": [],
    },
    {
        "nombre": "Básico",
        "precio": 4999,
        "duracion_dias": 30,
        "descripcion": "Accedé al mapa de ubicación para que los clientes te encuentren fácilmente.",
        "features": ["mapa_ubicacion"],
    },
    {
        "nombre": "VIP",
        "precio": 9999,
        "duracion_dias": 30,
        "descripcion": "Todo lo que necesitás: mapa, imágenes personalizadas y soporte prioritario.",
        "features": ["mapa_ubicacion", "imagenes_personalizadas", "soporte_prioritario"],
    },
]


def seed_planes():
    db = SessionLocal()
    try:
        if db.query(Plan).count() > 0:
            print("Ya existen planes cargados, saltando seed.")
            return

        for data in PLANES:
            features = data.pop("features")
            plan = Plan(**data)
            db.add(plan)
            db.flush()

            for feature_key in features:
                db.add(PlanFeature(id_plan=plan.id_plan, feature_key=feature_key))

        db.commit()
        print(f"✅ {len(PLANES)} planes cargados correctamente.")
    except SQLAlchemyError as e:
        db.rollback()
        print(f"❌ Error al cargar planes: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_planes()
