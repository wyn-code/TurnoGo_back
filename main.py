from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/test")
def test():
    return {"message": "Backend funcionando 🚀"}

@app.get("/categorias")
def listar_categorias():
    return [
        {"id": 1, "name": "Peluquería", "icon": "scissors"},
        {"id": 2, "name": "Spa", "icon": "sparkles"},
    ]