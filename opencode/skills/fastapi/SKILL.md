---
name: fastapi
description: Best practices for FastAPI, SQLAlchemy and PostgreSQL.
---

# FastAPI

Esta skill aplica al backend de TurnoGo.

## Arquitectura

Mantener la arquitectura existente.

No mover lógica de negocio a:

- routers
- controllers

La lógica pertenece a:

- services

## Endpoints

Antes de modificar un endpoint:

- Buscar quién lo consume.
- Revisar DTOs.
- Revisar schemas.
- Revisar modelos.
- Revisar validaciones.

No romper contratos existentes.

## SQLAlchemy

Antes de modificar modelos:

- Revisar relaciones.
- Revisar foreign keys.
- Revisar índices.
- Revisar cascadas.

Evitar consultas N+1.

## Base de datos

Siempre validar:

- integridad
- consistencia
- transacciones

No dejar datos inconsistentes.

## Validaciones

Toda validación importante debe realizarse en backend.

Nunca confiar en datos enviados por el frontend.

## Errores

Utilizar respuestas consistentes.

No devolver errores genéricos cuando pueda explicarse claramente la causa.

## Performance

Evitar:

- consultas repetidas
- consultas innecesarias
- cargar información que no se utiliza

## Antes de finalizar

Revisar:

- endpoints modificados
- services
- modelos
- schemas
- migraciones
- consultas SQLAlchemy