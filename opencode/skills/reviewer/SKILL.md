---
name: reviewer
description: Perform a complete code review before finishing any implementation.
---

# Reviewer

Antes de finalizar cualquier tarea, realizar una revisión completa del código modificado.

## Buscar errores

Revisar:

- bugs
- edge cases
- errores lógicos
- posibles race conditions
- problemas de concurrencia

## Código

Buscar:

- código duplicado
- funciones innecesarias
- archivos innecesarios
- imports sin usar
- variables sin usar
- código muerto

## Arquitectura

Verificar:

- que se respeten los patrones del proyecto
- que no se haya duplicado lógica
- que no existan dependencias circulares
- que la solución sea la más simple posible

## Frontend

Revisar:

- loading
- error state
- empty state
- disabled state
- navegación
- responsive
- accesibilidad básica

## Backend

Revisar:

- validaciones
- permisos
- manejo de errores
- consultas SQLAlchemy
- transacciones
- consistencia de datos

## Performance

Buscar:

- renders innecesarios
- consultas repetidas
- consultas N+1
- llamadas HTTP innecesarias

## Seguridad

Verificar:

- permisos
- validaciones
- datos sensibles
- tokens
- secretos
- variables de entorno

## Compatibilidad

Confirmar que los cambios no rompan funcionalidades existentes.

## Resultado

Antes de terminar:

1. Explicar qué archivos fueron modificados.
2. Explicar por qué fueron modificados.
3. Enumerar posibles riesgos.
4. Indicar mejoras futuras si las hubiera.