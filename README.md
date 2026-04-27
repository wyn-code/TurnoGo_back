# 📅 Sistema de Turnos SaaS

Aplicación web full stack para la gestión de turnos, desarrollada como proyecto final de la Tecnicatura Universitaria en Programación (UTN).

![Dashboard del Sistema](./dashboard.png)

---

## 🚀 Tecnologías utilizadas

**Frontend**
- React (gestión de estado y componentes)
- JavaScript / HTML / CSS

**Backend**
- Python 3
- FastAPI (API REST)

**Base de datos**
- SQL Server (diseño relacional, consultas optimizadas)

**Herramientas**
- Git / GitHub
- VS Code

---

## ✨ Funcionalidades principales

- Registro y autenticación de usuarios
- Gestión de turnos: creación, modificación y cancelación
- Validaciones de negocio (conflictos de horario, disponibilidad)
- Flujos de estado de turnos (pendiente → confirmado → cancelado)
- API REST documentada con FastAPI / Swagger
- Diseño de base de datos relacional normalizada

---

## 📸 Capturas de pantalla

| Vista principal | Gestión de turnos |
|---|---|
| ![Screenshot 1](./screenshots/screenshot1.png) | ![Screenshot 2](./screenshots/screenshot2.png) |

> _Agregá tus capturas en una carpeta `/screenshots` dentro del repositorio_

---

## ⚙️ Cómo correr el proyecto localmente

### Requisitos previos
- Python 3.10+
- Node.js 18+
- SQL Server (o instancia local)

### Backend

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/sistema-turnos-saas.git
cd sistema-turnos-saas/backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editá .env con tu cadena de conexión a SQL Server

# Correr el servidor
uvicorn main:app --reload
```

La API estará disponible en `http://localhost:8000`  
Documentación Swagger: `http://localhost:8000/docs`

### Frontend

```bash
cd ../frontend

# Instalar dependencias
npm install

# Correr la app
npm run dev
```

La app estará disponible en `http://localhost:5173`

---

## 🗂️ Estructura del proyecto

```
sistema-turnos-saas/
├── backend/
│   ├── main.py
│   ├── routers/
│   ├── models/
│   ├── schemas/
│   ├── database.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│   └── package.json
└── README.md
```

> _Ajustá esta estructura según cómo esté organizado tu proyecto real_

---

## 📖 API — Endpoints principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/auth/register` | Registro de usuario |
| POST | `/auth/login` | Login y obtención de token |
| GET | `/turnos` | Listar turnos del usuario |
| POST | `/turnos` | Crear nuevo turno |
| PUT | `/turnos/{id}` | Modificar turno |
| DELETE | `/turnos/{id}` | Cancelar turno |

---

## 👤 Autor

**Rocco Lavecchia**  
Full Stack Developer — React + FastAPI | Python & SQL

- 📧 roccolavecchia.rl@gmail.com  
- 💼 [LinkedIn](https://www.linkedin.com/in/rocco-lavecchia-58089917a/)  
- 🐙 [GitHub](https://github.com/tu-usuario)

---

## 📄 Licencia

Este proyecto fue desarrollado con fines educativos como proyecto final de carrera en la UTN.
