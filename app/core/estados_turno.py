
PENDIENTE = 1
CONFIRMADO = 2
COMPLETADO = 3
CANCELADO = 4
NO_ASISTIO = 5

NOMBRE_ESTADO = {
    PENDIENTE: "PENDIENTE",
    CONFIRMADO: "CONFIRMADO",
    COMPLETADO: "COMPLETADO",
    CANCELADO: "CANCELADO",
    NO_ASISTIO: "NO_ASISTIO",
}

# Transiciones válidas: estado_actual → [estados_finales_permitidos]
TRANSICIONES_PERMITIDAS: dict[int, list[int]] = {
    PENDIENTE: [CONFIRMADO, CANCELADO],
    CONFIRMADO: [COMPLETADO, CANCELADO, NO_ASISTIO],
}


def validar_transicion(estado_actual: int, nuevo_estado: int) -> bool:
    """Return True si la transición es permitida."""
    return nuevo_estado in TRANSICIONES_PERMITIDAS.get(estado_actual, [])
