from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.db.database import engine

from app.routers.auth_router import router as auth_router
from app.routers.categoria_router import router as categoria_router
from app.routers.empleado_router import router as empleado_router
from app.routers.negocio_router import router as negocio_router
from app.routers.servicio_router import router as servicio_router
from app.routers.turno_router import router as turno_router
from app.routers.usuario_router import router as usuario_router
from app.routers.cliente_router import router as cliente_router
from app.routers.horarios_negocio_router import router as horarios_negocio_router
from app.routers.georef_router import router as georef_router


def create_app():
    app = FastAPI(title="Turnexo")

    origins = [
        "http://localhost:5173",
        "https://www.turnogo.app/"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", summary="Healthcheck")
    def root():
        return {"mensaje": "API Turnexo funcionando 🚀"}

    @app.get("/test")
    def test():
        return {"message": "Backend funcionando 🚀"}

    @app.get("/db-test", summary="Prueba conexión DB")
    def test_db():
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT 'conexion OK con postgres'")
            )
            return {"resultado": result.scalar()}

    @app.get("/categorias")
    def listar_categorias():
        return [
            {"id": 1, "name": "Peluquería", "icon": "scissors"},
            {"id": 2, "name": "Spa", "icon": "sparkles"},
        ]

    app.include_router(usuario_router, prefix="/api", tags=["Usuarios"])
    app.include_router(auth_router, prefix="/api")
    app.include_router(turno_router, prefix="/api", tags=["Turnos"])
    app.include_router(empleado_router, prefix="/api", tags=["Empleados"])
    app.include_router(servicio_router, prefix="/api")
    app.include_router(negocio_router, prefix="/api")
    app.include_router(categoria_router, prefix="/api", tags=["Categorias"])
    app.include_router(cliente_router, prefix="/api", tags=["Clientes"])
    app.include_router(horarios_negocio_router, prefix="/api", tags=["Horarios"])
    app.include_router(georef_router, prefix="/api", tags=["Georef"])

    return app


app = create_app()