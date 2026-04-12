from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

# 🔥 DB
from app.db.database import engine
from app.db.base import Base

# 🔥 IMPORTAR MODELOS (CLAVE para crear tablas)
from app.models.categoria import Categoria

# 🔥 Routers
from app.routers import (
    auth_router,
    categoria_router,
    empleado_router,
    negocio_router,
    servicio_router,
    turno_router,
    usuario,
)

app = FastAPI(title="Turnexo")

# 🔥 Crear tablas automáticamente
Base.metadata.create_all(bind=engine)

# 🔥 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 Healthcheck
@app.get("/", summary="Healthcheck")
def root():
    return {"mensaje": "API Turnexo funcionando"}

# 🔥 Test DB
@app.get("/db-test", summary="Prueba conexión DB")
def test_db():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 'conexion OK con postgres'"))
        return {"resultado": result.scalar()}

# 🔥 Routers
app.include_router(usuario.router, prefix="/api", tags=["Usuarios"])
app.include_router(auth_router.router, prefix="/api")
app.include_router(turno_router.router, prefix="/api", tags=["Turnos"])
app.include_router(empleado_router.router, prefix="/api", tags=["Empleados"])
app.include_router(servicio_router.router, prefix="/api")
app.include_router(negocio_router.router, prefix="/api")
app.include_router(categoria_router.router, prefix="/api", tags=["Categorias"])
