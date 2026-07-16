import io

import qrcode

from app.core.config import FRONTEND_URL


def generar_qr_url(id_turno: int) -> str:
    """Build the scan URL encoded in the QR."""
    return f"{FRONTEND_URL}/dashboard/turnos?turno={id_turno}"


def generar_qr_png_bytes(id_turno: int) -> bytes:
    """Generate a QR image for *id_turno* and return raw PNG bytes."""
    payload = generar_qr_url(id_turno)

    img = qrcode.make(payload, box_size=8, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")

    return buf.getvalue()
