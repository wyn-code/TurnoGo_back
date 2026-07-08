# Documentación del Proyecto Turnexo

## Índice
1. [Arquitectura General](#1-arquitectura-general)
2. [Base de Datos (Supabase / PostgreSQL)](#2-base-de-datos-supabase--postgresql)
3. [Backend (FastAPI + Python)](#3-backend-fastapi--python)
4. [Frontend (React + Vite + TypeScript)](#4-frontend-react--vite--typescript)
5. [Flujos Principales](#5-flujos-principales)
6. [Despliegue y Entornos](#6-despliegue-y-entornos)

---

## 1. Arquitectura General

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (Vite)                    │
│              React 19 + TypeScript                   │
│              http://localhost:5173                    │
└──────────────────────┬──────────────────────────────┘
                       │  REST API (JSON)
                       │  http://localhost:8000/api/*
                       ▼
┌─────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                    │
│              Python + SQLAlchemy ORM                  │
│              http://localhost:8000                     │
└──────────────────────┬──────────────────────────────┘
                       │  SQL (psycopg2)
                       ▼
┌─────────────────────────────────────────────────────┐
│           Supabase PostgreSQL (Cloud)                 │
│   aws-1-us-east-1.pooler.supabase.com:5432            │
└─────────────────────────────────────────────────────┘
```

**Flujo de datos:** El frontend **nunca se conecta directamente a Supabase**. Siempre habla con el backend vía REST. El backend es el único que tiene acceso a la base de datos.

---

## 2. Base de Datos (Supabase / PostgreSQL)

### 2.1 Conexión

La conexión se define en el archivo `.env` del backend:

```
DB=postgresql://postgres.avbxctvdivlejrdlfijx:Turnexo123-@aws-1-us-east-1.pooler.supabase.com:5432/postgres
```

El backend lee esta variable en `app/db/database.py`:

```python
DATABASE_URL = config('DB')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

Usa **connection pooling** de Supabase (`pooler.supabase.com`).

### 2.2 Tablas

| Tabla | Modelo (SQLAlchemy) | Propósito |
|-------|---------------------|-----------|
| `usuarios` | `Usuario` | Dueños de negocio y admins |
| `negocio` | `Negocio` | Negocios registrados |
| `categorias` | `Categoria` | Categorías de negocio |
| `servicio` | `Servicio` | Servicios que ofrece cada negocio |
| `empleado` | `Empleado` | Empleados de cada negocio |
| `turno` | `Turno` | Turnos/reservas |
| `estado_turno` | `EstadoTurno` | Estados posibles de un turno |
| `cliente` | `Cliente` | Clientes que reservan |
| `horarios_negocio` | `HorarioNegocio` | Horarios de atención |
| `negocio_imagen` | `NegocioImagen` | Imágenes del negocio |
| `planes` | `Plan` | Planes de suscripción (Free, Básico, VIP) |
| `plan_features` | `PlanFeature` | Features habilitadas por plan |
| `suscripciones` | `Suscripcion` | Suscripciones activas de cada negocio |
| `provincia` | `Provincia` | Provincias argentinas |
| `localidades` | `Localidad` | Localidades argentinas |
| `metodo_pago` | `MetodoPago` | Métodos de pago |

### 2.3 Migraciones

- **Supabase SQL** (`supabase/migrations/`): 6 archivos `.sql` con el esquema inicial y cambios estructurales.
- **Alembic** (`alembic/versions/`): 1 migración Python para cambios en la tabla `categorias`.

### 2.4 Seed Data

El backend ejecuta seeds al iniciar para crear datos precargados:

**seed_planes()**: Crea 3 planes de suscripción:
| Plan | Precio | Duración | Features |
|------|--------|----------|----------|
| Free | $0 | — | (ninguna) |
| Básico | $4.999 | 30 días | mapa_ubicacion |
| VIP | $9.999 | 30 días | mapa_ubicacion, imagenes_personalizadas, soporte_prioritario |

**seed_provincias()**: Crea las 24 provincias argentinas.

---

## 3. Backend (FastAPI + Python)

### 3.1 Estructura de Carpetas

```
app/
├── main.py                 # Entry point, monta routers, configura CORS
├── core/
│   ├── config.py           # Variables de entorno (SECRET_KEY, APIs, etc.)
│   ├── dependencies.py     # get_db(), get_current_user(), require_feature()
│   └── security.py         # Creación y verificación de JWT
├── db/
│   ├── database.py         # Conexión a PostgreSQL (via python-decouple)
│   ├── session.py          # Conexión alternativa (via python-dotenv)
│   ├── base.py             # declarative_base() de SQLAlchemy
│   └── seeds/
│       ├── seed_planes.py
│       └── seed_provincias.py
├── models/                 # Modelos SQLAlchemy (1 por tabla)
├── schemas/                # Schemas Pydantic (request/response)
├── routers/                # Routers FastAPI (endpoints)
└── services/               # Lógica de negocio
```

### 3.2 Endpoints por Router

| Router | Prefijo | Endpoints Clave |
|--------|---------|-----------------|
| `auth_router` | `/api/auth` | `POST /register`, `POST /login`, `GET /me`, `POST /forgot-password`, `GET /verify-email/{token}` |
| `usuario_router` | `/api/usuarios` | CRUD de usuarios (admin) |
| `negocio_router` | `/api/negocios` | CRUD de negocios, `POST /complete`, `GET /slug/{slug}`, `GET /mapa` |
| `categoria_router` | `/api/categorias` | CRUD de categorías |
| `servicio_router` | `/api/servicios` | CRUD de servicios |
| `empleado_router` | `/api/empleados` | CRUD de empleados |
| `turno_router` | `/api/turnos` | CRUD de turnos, `GET /por-rango` |
| `cliente_router` | `/api/clientes` | CRUD de clientes, `POST /get-or-create` |
| `horarios_router` | `/api/horarios` | CRUD de horarios |
| `georef_router` | `/api/georef` | `GET /provincias`, `GET /localidades` (proxy a API Argentina) |
| `plan_router` | `/api/planes` | `GET /` (listar planes), `GET /negocios/{id}/funciones` |
| `pago_router` | `/api/pagos` | `POST /crear-preferencia`, `GET /suscripcion/actual`, `POST /cancelar`, `PUT /renovacion-automatica`, `POST /webhook` |

### 3.3 Autenticación (JWT)

Usa **JWT** con `python-jose`:

1. **Login**: `POST /api/auth/login` → devuelve `access_token`
2. **Verificación**: cada request protegido incluye `Authorization: Bearer <token>`
3. **Dependencia**: `get_current_user()` decodifica el token y devuelve el `Usuario`
4. **Expiración**: configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 60 min)

**Flujo de registro con verificación de email:**

1. `POST /api/auth/register` → crea usuario con `email_verified=False`
2. Envía email de verificación vía **Resend**
3. Usuario hace clic en link → `GET /api/auth/verify-email/{token}` → marca como verificado y devuelve JWT

### 3.4 Sistema de Membresía

1. **Planes**: definidos en DB (tabla `planes` + `plan_features`)
2. **Suscripción**: al pagar vía MercadoPago, se crea un registro en `suscripciones`
3. **Features**: `plan_service.obtener_funciones_negocio()` consulta qué features tiene el negocio según su suscripción activa
4. **Guard**: `require_feature(feature_key)` es una dependencia FastAPI que bloquea endpoints si el negocio no tiene la feature

### 3.5 Pagos (MercadoPago)

1. Backend crea una **preferencia de pago** en MercadoPago → devuelve `init_point`
2. Frontend redirige al usuario a la URL de checkout de MercadoPago
3. MercadoPago redirige de vuelta al frontend: `/pagos/resultado?status=approved|failure|pending`
4. **Webhook**: MercadoPago notifica al backend (`POST /api/pagos/webhook`) cuando el pago se aprueba
5. Backend marca la suscripción como activa

### 3.6 Tests

Usan **SQLite en memoria** (no tocan Supabase). Framework: **Pytest** + `TestClient` de FastAPI.

```
cd Turnexo
pytest -v
```

Archivos de test: `tests/test_auth_service.py`, `test_categorias.py`, `test_negocios.py`, `test_turnos.py`, `test_plan_router.py`, `test_plan_service.py`, `test_pago_router.py`, `test_pago_service.py`, `test_negocio_membresia.py`.

---

## 4. Frontend (React + Vite + TypeScript)

### 4.1 Estructura

```
src/
├── main.tsx                  # Entry point
├── App.tsx                   # Providers + routing
├── components/
│   ├── ui/                   # 51 componentes shadcn/ui (Radix primitives)
│   └── NavLink.tsx
├── features/                 # Organización por dominio
│   ├── auth/                 # Login, registro, verificación email
│   ├── landing/              # Landing page (Navbar, Hero, Footer, etc.)
│   ├── business/             # Perfil público del negocio + listado
│   ├── booking/              # Flujo de reserva de turnos
│   ├── dashboard/            # Panel de administración del negocio
│   ├── membership/           # Planes, suscripción, pagos
│   ├── register-business/    # Wizard de registro (7 pasos)
│   ├── admin/                # Panel de administración global
│   └── marketplace/          # Búsqueda y filtros
├── hooks/                    # React Query hooks compartidos
├── lib/                      # api-client, api-config, cloudinary, utils
├── services/                 # Servicios compartidos
└── types/api.ts              # Interfaces TypeScript
```

### 4.2 Árbol de Providers

```
QueryClientProvider          ← TanStack React Query
  TooltipProvider            ← shadcn/ui
    Toaster + Sonner         ← Notificaciones
    BrowserRouter
      AuthProvider           ← AuthContext (user, token, login, logout)
        MembershipProvider   ← MembershipContext (plan, features)
          Suspense           ← Lazy loading
            AppRoutes        ← React Router
```

### 4.3 API Client

Cliente HTTP propio basado en `fetch()` ubicado en `lib/api-client.ts`:
- Mantiene el token JWT en memoria
- Agrega automáticamente `Authorization: Bearer <token>`
- Agrega `Content-Type: application/json` (excepto para FormData)
- En 401 redirige a `/login`
- Métodos: `get`, `post`, `put`, `patch`, `delete`

```typescript
const planes = await apiClient.get<ApiPlan[]>("/planes/");
```

### 4.4 Rutas

| Ruta | Componente | Protegida |
|------|-----------|-----------|
| `/` | Landing (Index) | No |
| `/negocios` | Listado de negocios | No |
| `/negocio/:slug` | Perfil del negocio | No |
| `/reservar/:slug` | Reservar turno | No |
| `/login` | Inicio de sesión | No |
| `/registro` | Registro | No |
| `/planes` | Planes | Sí |
| `/mi-suscripcion` | Mi Suscripción | Sí |
| `/pagos/resultado` | Post-pago | No |
| `/dashboard/*` | Dashboard del negocio | Sí |
| `/registrar-negocio` | Registrar negocio | Sí |
| `/admin/*` | Admin global | Solo admin |

### 4.5 Dashboard

Rutas anidadas bajo `/dashboard/*`:

| Ruta | Propósito |
|------|-----------|
| `/dashboard` | Resumen / estadísticas |
| `/dashboard/turnos` | Gestión de turnos recibidos |
| `/dashboard/servicios` | CRUD de servicios |
| `/dashboard/empleados` | CRUD de empleados |
| `/dashboard/horarios` | Horarios de atención |
| `/dashboard/configuracion` | Datos del negocio |
| `/dashboard/personalizacion` | Personalización premium |

### 4.6 Wizard de Registro de Negocio (7 pasos)

1. **Info básica** → nombre, categoría, descripción
2. **Imágenes** → logo + galería de imágenes
3. **Contacto** → WhatsApp, teléfono, Instagram
4. **Ubicación** → dirección, ciudad, provincia
5. **Servicios** → lista dinámica de servicios
6. **Empleados** → lista dinámica de empleados
7. **Horarios** → grilla semanal de horarios

Al finalizar se envía todo en un solo `POST /api/negocios/complete`.

### 4.7 Tecnologías

| Librería | Versión | Uso |
|----------|---------|-----|
| React | 19 | UI |
| TypeScript | ~5.9 | Tipado estático |
| Vite | 8 | Build / dev server |
| React Router | 7 | Enrutamiento |
| TanStack React Query | 5 | Data fetching + caché |
| Tailwind CSS | 3 | Estilos |
| shadcn/ui + Radix | — | Componentes de UI |
| lucide-react | — | Iconos |
| date-fns | 4 | Fechas |
| react-hook-form + zod | — | Formularios + validación |
| sonner | — | Toast notifications |
| MercadoPago SDK | — | Pagos |
| Mapbox GL JS | 3 | Mapas |

---

## 5. Flujos Principales

### 5.1 Registro + Creación de Negocio

```
Registro → POST /auth/register → Email verificación
  → Clic en link → VerifyEmailPage → loginWithToken()
  → Redirige a /registrar-negocio
  → Wizard 7 pasos → POST /negocios/complete
  → Redirige a /dashboard
```

### 5.2 Reserva de Turno

```
Navega a /negocio/:slug → Ve perfil + servicios
  → Clic "Reservar" → /reservar/:slug
  → BookingStepper: servicio → empleado → fecha/hora → datos cliente
  → POST /turnos → Turno creado
```

### 5.3 Suscripción a un Plan

```
/dashboard → /planes → Ve planes
  → Clic "Suscribirse" → POST /pagos/crear-preferencia
  → Recibe init_point → Redirige a MercadoPago
  → Paga → /pagos/resultado?status=approved
  → MembershipContext.refresh() → Features activadas
```

### 5.4 Verificación de Features

**Backend:** `require_feature("mapa_ubicacion")` → `plan_service.negocio_tiene_funcion()` → SQL → HTTP 403 si no tiene la feature.

**Frontend:** `<FeatureGuard featureKey="mapa_ubicacion">` → `MembershipContext.tieneFuncion()` → Renderiza children o upgrade banner.

---

## 6. Desarrollo Local

### 6.1 Variables de Entorno

**Backend** (`.env`):
```
DB=postgresql://...
SECRET_KEY=...
RESEND_API_KEY=...
MAPBOX_ACCESS_TOKEN=...
MERCADOPAGO_ACCESS_TOKEN=...
BACKEND_URL=...
```

**Frontend** (`.env.local`):
```
VITE_API_URL=http://localhost:8000
VITE_MAPBOX_TOKEN=...
VITE_CLOUDINARY_CLOUD_NAME=...
VITE_CLOUDINARY_UPLOAD_PRESET=...
```

### 6.2 Iniciar Proyecto

```bash
# Backend
cd Turnexo
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd Turnexo_front
npm install
npm run dev
```

### 6.3 Comandos Útiles

```bash
# Tests backend
cd Turnexo && pytest -v

# Typecheck frontend
cd Turnexo_front && npx tsc --noEmit

# Build frontend para producción
cd Turnexo_front && npm run build
```
