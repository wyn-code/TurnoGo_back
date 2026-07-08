# Changelog — Turnogo

## Limpieza general

### Fase 1 — Repositorio
- **1.2** — Agregado `*.db` al `.gitignore` y eliminados `test.db` (raíz + `app/`)
- **1.4** — Renombrado `tests/auth.py` → `tests/auth_helpers.py` (no seguía convención `test_*.py`)
- Eliminada carpeta `htmlcov/` (reporte de coverage autogenerado)
- Movidos 5 archivos `.txt`/`.docx` de la raíz a `docs/`
- Eliminado `requirements.txt` duplicado en la raíz del proyecto

### Fase 3 — Código
- **3.1** — Eliminado endpoint `/test` duplicado en `main.py`
- **3.2** — Renombrado proyecto: `Turnexo` → `Turnogo` en `main.py`, `email_service.py`, `turno_service.py`
- Eliminados endpoints `/categorias` (mock hardcodeado) y `/test` (redundante) de `main.py`
- Corregido import: `import sqlalchemy` → `from sqlalchemy import text`
- Agregados `tags` faltantes en routers: Auth, Servicios, Negocios

### Fase 4 — Tests
- Corregido import desactualizado `from .auth` → `from tests.auth_helpers` en 5 archivos
- Corregido payload del test `test_owner_no_puede_crear_servicio_en_negocio_ajeno` (campos incorrectos)
- Eliminado test `test_owner_no_puede_acceder_dashboard_privado_ajeno` (endpoint inexistente)
- **70 tests pasando, 0 fallos**

### Fase 5 — Dependencias
- Versiones relajadas: `==` → `>=` en `requirements.txt`
- Eliminado `uvloop` (no compatible con Windows)
- Agregado `pylint` como dependencia de desarrollo

### Otros
- `htmlcov/`, `.coverage`, `.pytest_cache/`, `.agents/` agregados al `.gitignore`
- README actualizado: título "Turnogo", PostgreSQL (Supabase) en vez de SQL Server
- Eliminados ~20 `print()` de debug en services, routers y database
- Actualizado `database.py` para silenciar prints de conexión
