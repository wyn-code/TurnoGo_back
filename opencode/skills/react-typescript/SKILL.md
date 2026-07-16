---
name: react-typescript
description: Best practices for React, TypeScript, Vite and React Query.
---

# React + TypeScript

Esta skill aplica a todo el frontend de TurnoGo.

## Antes de modificar

- Analizar el flujo completo antes de escribir código.
- Buscar componentes relacionados.
- Buscar hooks relacionados.
- Buscar services relacionados.
- Buscar tipos relacionados.
- Buscar páginas relacionadas.

## Componentes

- Mantener componentes pequeños y reutilizables.
- No duplicar componentes existentes.
- Extraer componentes solo cuando realmente agreguen valor.
- Mantener consistencia con el proyecto.

## Estado

- Evitar estados duplicados.
- Derivar estado cuando sea posible.
- No guardar información que pueda calcularse.

## React Query

- Reutilizar queries existentes.
- Invalidar únicamente las queries necesarias.
- Evitar refetch innecesarios.
- Mantener sincronizado el cache.

## TypeScript

- Nunca usar any.
- Aprovechar los tipos existentes.
- Reutilizar interfaces y DTOs.
- Mantener tipado fuerte.

## Servicios

- Toda llamada HTTP debe pasar por los services existentes.
- No hacer fetch directo dentro de componentes.
- Mantener una separación clara entre UI y lógica.

## UI

Siempre considerar:

- loading
- error state
- empty state
- disabled state
- feedback al usuario

## Performance

Evitar:

- renders innecesarios
- useEffect innecesarios
- lógica pesada dentro del render
- recrear funciones constantemente

## Antes de finalizar

Verificar:

- TypeScript
- imports sin usar
- componentes afectados
- React Query
- navegación
- responsive