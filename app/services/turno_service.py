from datetime import datetime, timedelta, UTC

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.servicio import Servicio
from app.models.turnos import Turno
from app.schemas.appointment_schema import TurnoActualizar, TurnoCrear


SOLAPAMIENTO_DETALLE = "El empleado ya tiene un turno en ese horario"


def listar_turnos(db: Session):
    return db.query(Turno).all()


def obtener_turno_por_id(db: Session, turno_id: int):
    return db.query(Turno).filter(Turno.id_turno == turno_id).first()


def obtener_servicio_o_404(db: Session, id_servicio: int):
    servicio = db.query(Servicio).filter(
        Servicio.id_servicio == id_servicio
    ).first()

    if not servicio:
        raise HTTPException(status_code=404, detail="El servicio no existe")

    return servicio


def validar_rango_horario(inicio: datetime, fin: datetime | None):
    if fin is not None and fin <= inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha_hora_fin debe ser mayor que la fecha_hora_inicio"
        )


def hay_superposicion(
    db: Session,
    id_empleado: int,
    inicio: datetime,
    fin: datetime | None,
    excluir_turno_id: int | None = None,
):
    if fin is None:
        return False

    query = db.query(Turno).filter(
        Turno.id_empleado == id_empleado,
        Turno.fecha_hora_inicio < fin,
        Turno.fecha_hora_fin > inicio
    )

    if excluir_turno_id is not None:

        query = query.filter(Turno.id_turno != excluir_turno_id)

    return query.first() is not None


def _resolver_fecha_hora_fin(
    db: Session,
    id_servicio: int,
    fecha_hora_inicio: datetime,
    fecha_hora_fin: datetime | None,
) -> datetime:
    if fecha_hora_fin is not None:
        return fecha_hora_fin

    servicio = obtener_servicio_o_404(db, id_servicio)
    return fecha_hora_inicio + timedelta(minutes=servicio.duracion_min)


def _lanzar_error_integridad(e: IntegrityError) -> None:
    error_text = str(e.orig)
    if "ex_turno_no_solapa_por_empleado" in error_text:
        raise HTTPException(
            status_code=409, detail=SOLAPAMIENTO_DETALLE) from e

    raise HTTPException(
        status_code=400,
        detail=f"Error de integridad en la base de datos: {error_text}"
    ) from e


def crear_turno(db: Session, turno: TurnoCrear):
    fecha_hora_fin = _resolver_fecha_hora_fin(
        db=db,
        id_servicio=turno.id_servicio,
        fecha_hora_inicio=turno.fecha_hora_inicio,
        fecha_hora_fin=turno.fecha_hora_fin,
    )

    if fecha_hora_fin <= turno.fecha_hora_inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha_hora_fin debe ser mayor que la fecha_hora_inicio"
        )

    validar_rango_horario(turno.fecha_hora_inicio, fecha_hora_fin)

    if hay_superposicion(
        db,
        turno.id_empleado,
        turno.fecha_hora_inicio,
        fecha_hora_fin
    ):
        raise HTTPException(
            status_code=409,
            detail=SOLAPAMIENTO_DETALLE
        )

    ahora = datetime.now(UTC)

    nuevo_turno = Turno(
        id_negocio=turno.id_negocio,
        id_cliente=turno.id_cliente,
        id_servicio=turno.id_servicio,
        id_estado=turno.id_estado,
        id_empleado=turno.id_empleado,
        fecha_hora_inicio=turno.fecha_hora_inicio,
        fecha_hora_fin=fecha_hora_fin,
        id_admin_aprobador=None,
        aprobado_at=None,
        rechazado_motivo=None,
        created_at=ahora,
        updated_at=ahora,
    )

    try:
        db.add(nuevo_turno)
        db.commit()
        db.refresh(nuevo_turno)
        return nuevo_turno

    except IntegrityError as e:
        db.rollback()
        _lanzar_error_integridad(e)


def actualizar_turno(db: Session, turno_id: int, datos: TurnoActualizar):
    turno_db = db.query(Turno).filter(Turno.id_turno == turno_id).first()

    if not turno_db:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    nuevo_id_servicio = (
        datos.id_servicio if datos.id_servicio is not None else turno_db.id_servicio
    )
    nuevo_id_empleado = (
        datos.id_empleado if datos.id_empleado is not None else turno_db.id_empleado
    )
    nueva_fecha_inicio = (
        datos.fecha_hora_inicio
        if datos.fecha_hora_inicio is not None
        else turno_db.fecha_hora_inicio
    )

    recalcular_fin = datos.id_servicio is not None or datos.fecha_hora_inicio is not None
    nueva_fecha_fin = (
        _resolver_fecha_hora_fin(
            db=db,
            id_servicio=nuevo_id_servicio,
            fecha_hora_inicio=nueva_fecha_inicio,
            fecha_hora_fin=datos.fecha_hora_fin,
        )
        if recalcular_fin or datos.fecha_hora_fin is not None
        else turno_db.fecha_hora_fin
    )

    if nueva_fecha_fin is not None and nueva_fecha_fin <= nueva_fecha_inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha_hora_fin debe ser mayor que la fecha_hora_inicio"
        )

    validar_rango_horario(nueva_fecha_inicio, nueva_fecha_fin)

    if hay_superposicion(
        db,
        nuevo_id_empleado,
        nueva_fecha_inicio,
        nueva_fecha_fin,
        excluir_turno_id=turno_id
    ):
        raise HTTPException(
            status_code=409,
            detail=SOLAPAMIENTO_DETALLE
        )

    turno_db.id_negocio = (
        datos.id_negocio if datos.id_negocio is not None else turno_db.id_negocio
    )
    turno_db.id_cliente = (
        datos.id_cliente if datos.id_cliente is not None else turno_db.id_cliente
    )
    turno_db.id_servicio = nuevo_id_servicio
    turno_db.id_estado = (
        datos.id_estado if datos.id_estado is not None else turno_db.id_estado
    )
    turno_db.id_empleado = nuevo_id_empleado
    turno_db.fecha_hora_inicio = nueva_fecha_inicio
    turno_db.fecha_hora_fin = nueva_fecha_fin

    if datos.id_admin_aprobador is not None:
        turno_db.id_admin_aprobador = datos.id_admin_aprobador
    if datos.aprobado_at is not None:
        turno_db.aprobado_at = datos.aprobado_at
    if datos.rechazado_motivo is not None:
        turno_db.rechazado_motivo = datos.rechazado_motivo

    turno_db.updated_at = datetime.now(UTC)

    try:
        db.commit()
        db.refresh(turno_db)
        return turno_db

    except IntegrityError as e:
        db.rollback()
        _lanzar_error_integridad(e)


def borrar_turno(db: Session, turno_id: int):
    turno_db = db.query(Turno).filter(Turno.id_turno == turno_id).first()

    if not turno_db:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    try:
        db.delete(turno_db)
        db.commit()
        return turno_db

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar el turno: {str(e)}"
        )
