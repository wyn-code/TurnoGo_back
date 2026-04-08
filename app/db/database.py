from app.db.base import Base  # 👈 correcto

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from decouple import config

DATABASE_URL = config('DB')

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Test de conexión (opcional)
try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        print("Conexión a PostgreSQL exitosa")
except OperationalError as e:
    print("Error de conexión:", e)