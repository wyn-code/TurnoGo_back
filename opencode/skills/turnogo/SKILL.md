---
name: turnogo
description: Rules specific to the TurnoGo SaaS project.
compatibility: opencode
---

# TurnoGo Project Rules

Este proyecto utiliza:

Frontend:
- React
- TypeScript
- Vite
- Tailwind
- React Query

Backend:
- FastAPI
- SQLAlchemy
- PostgreSQL

Antes de modificar:

- Analizar el flujo completo.
- Buscar componentes relacionados.
- Buscar servicios relacionados.
- Buscar endpoints relacionados.

Nunca:

- Duplicar lógica.
- Crear componentes innecesarios.
- Romper el tipado.
- Cambiar nombres de endpoints existentes.

Siempre:

- Mantener consistencia.
- Explicar los cambios.
- Revisar TypeScript.
- Revisar ESLint.

Cuando se modifique el flujo de reservas:

Analizar:

- UI
- Service
- API
- Backend
- Base de datos

Antes de escribir código.