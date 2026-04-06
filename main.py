from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import negocio_router, turno_router, empleado_router, servicio_router, usuario

app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ← Registrar los routers
app.include_router(negocio_router.router, prefix="/api")
app.include_router(turno_router.router, prefix="/api")
app.include_router(empleado_router.router, prefix="/api")
app.include_router(servicio_router.router, prefix="/api")
app.include_router(usuario.router, prefix="/api")

@app.get("/test")
def test():
    return {"message": "Backend funcionando 🚀"}

@app.get("/categorias")
def listar_categorias():
    return [
        {"id": 1, "name": "Peluquería", "icon": "scissors"},
        {"id": 2, "name": "Spa", "icon": "sparkles"},
    ]