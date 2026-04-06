from app.db.base import SessionLocal
from app.models.provincia import Provincia
from sqlalchemy.exc import SQLAlchemyError

PROVINCIAS = [
    "Buenos Aires",
    "Ciudad Autónoma de Buenos Aires",
    "Catamarca",
    "Chaco",
    "Chubut",
    "Córdoba",
    "Corrientes",
    "Entre Ríos",
    "Formosa",
    "Jujuy",
    "La Pampa",
    "La Rioja",
    "Mendoza",
    "Misiones",
    "Neuquén",
    "Río Negro",
    "Salta",
    "San Juan",
    "San Luis",
    "Santa Cruz",
    "Santa Fe",
    "Santiago del Estero",
    "Tierra del Fuego",
    "Tucumán",
]


def seed_provincias():
    db = SessionLocal()
    try:
        # Evita duplicados si corrés el script más de una vez
        if db.query(Provincia).count() > 0:
            print("Ya existen provincias cargadas, saltando seed.")
            return

        for nombre in PROVINCIAS:
            db.add(Provincia(nombre=nombre))

        db.commit()
        print(f"✅ {len(PROVINCIAS)} provincias cargadas correctamente.")
    except SQLAlchemyError as e:
        db.rollback()
        print(f"❌ Error al cargar provincias: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_provincias()
