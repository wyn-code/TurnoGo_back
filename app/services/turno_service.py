from datetime import UTC, datetime, timedelta

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.empleado import Empleado
from app.models.horarios_negocio import HorarioNegocio
from app.models.negocio import Negocio
from app.models.servicio import Servicio
from app.models.turnos import Turno
from app.schemas.appointment_schema import TurnoActualizar, TurnoCrear
# 🔥 Importamos tu nuevo servicio de Twilio


SOLAPAMIENTO_DETALLE = "El empleado ya tiene un turno en ese horario"

# Ajustá estos IDs según tus registros reales de estado_turno
ESTADO_PENDIENTE_CONFIRMACION_CLIENTE = 1
ESTADO_PENDIENTE_APROBACION = 2
ESTADO_CONFIRMADO = 3


def listar_turnos(db: Session):
    return db.query(Turno).all()


def obtener_turno_por_id(db: Session, turno_id: int):
    return db.query(Turno).filter(Turno.id_turno == turno_id).first()


def obtener_servicio_del_negocio(db: Session, id_servicio: int, id_negocio: int):
    servicio = (
        db.query(Servicio)
        .join(Negocio, Negocio.id_negocio == Servicio.id_negocio)
        .filter(
            Servicio.id_servicio == id_servicio,
            Servicio.id_negocio == id_negocio,
            Servicio.activo.is_(True),
            Negocio.activo.is_(True),
        )
        .first()
    )

    if not servicio:
        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado para el negocio indicado o negocio inactivo",
        )

    return servicio


def validar_empleado_del_negocio(
    db: Session,
    id_negocio: int,
    id_empleado: int | None,
):
    if id_empleado is None:
        return

    empleado = db.query(Empleado).filter(
        Empleado.id_empleado == id_empleado,
        Empleado.id_negocio == id_negocio,
        Empleado.activo.is_(True),
    ).first()

    if not empleado:
        raise HTTPException(
            status_code=400,
            detail="Empleado no encontrado para el negocio indicado",
        )


def validar_turno_dentro_del_horario(
    db: Session,
    id_negocio: int,
    inicio: datetime,
    fin: datetime,
):
    horarios = db.query(HorarioNegocio).filter(
        HorarioNegocio.id_negocio == id_negocio
    ).all()

    if not horarios:
        return

    dias_semana_validos = {inicio.weekday(), inicio.isoweekday()}
    hora_inicio = inicio.time()
    hora_fin = fin.time()

    for horario in horarios:
        if (
            horario.dia_semana in dias_semana_validos
            and horario.hora_apertura <= hora_inicio
            and hora_fin <= horario.hora_cierre
        ):
            return

    raise HTTPException(
        status_code=400,
        detail="El turno está fuera del horario de atención del negocio",
    )


def validar_rango_horario(inicio: datetime, fin: datetime | None):
    if fin is not None and fin <= inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha_hora_fin debe ser mayor que la fecha_hora_inicio",
        )


def hay_superposicion(
    db: Session,
    id_negocio: int,
    id_empleado: int | None,
    inicio: datetime,
    fin: datetime | None,
    excluir_turno_id: int | None = None,
):
    if fin is None:
        return False

    query = db.query(Turno).filter(
        Turno.id_negocio == id_negocio,
        Turno.fecha_hora_inicio < fin,
        Turno.fecha_hora_fin > inicio,
    )

    if id_empleado is not None:
        query = query.filter(Turno.id_empleado == id_empleado)

    if excluir_turno_id is not None:
        query = query.filter(Turno.id_turno != excluir_turno_id)

    return query.first() is not None


def _resolver_fecha_hora_fin(
    db: Session,
    id_servicio: int,
    id_negocio: int,
    fecha_hora_inicio: datetime,
    fecha_hora_fin: datetime | None = None,
) -> datetime:
    if fecha_hora_fin is not None:
        return fecha_hora_fin

    servicio = obtener_servicio_del_negocio(
        db=db,
        id_servicio=id_servicio,
        id_negocio=id_negocio,
    )
    return fecha_hora_inicio + timedelta(minutes=servicio.duracion_min)


def _resolver_estado_inicial(servicio: Servicio) -> int:
    return (
        ESTADO_PENDIENTE_APROBACION
        if servicio.requiere_aprobacion
        else ESTADO_PENDIENTE_CONFIRMACION_CLIENTE
    )


def _lanzar_error_integridad(e: IntegrityError) -> None:
    error_text = str(e.orig)

    if "ex_turno_no_solapa_por_empleado" in error_text:
        raise HTTPException(
            status_code=409,
            detail=SOLAPAMIENTO_DETALLE,
        ) from e

    raise HTTPException(
        status_code=400,
        detail=f"Error de integridad en la base de datos: {error_text}",
    ) from e


def crear_turno(db: Session, turno: TurnoCrear, background_tasks: BackgroundTasks):
    servicio = obtener_servicio_del_negocio(
        db=db,
        id_servicio=turno.id_servicio,
        id_negocio=turno.id_negocio,
    )

    fecha_hora_fin = _resolver_fecha_hora_fin(
        db=db,
        id_servicio=turno.id_servicio,
        id_negocio=turno.id_negocio,
        fecha_hora_inicio=turno.fecha_hora_inicio,
    )

    validar_rango_horario(turno.fecha_hora_inicio, fecha_hora_fin)
    validar_empleado_del_negocio(
        db=db,
        id_negocio=turno.id_negocio,
        id_empleado=turno.id_empleado,
    )
    validar_turno_dentro_del_horario(
        db=db,
        id_negocio=turno.id_negocio,
        inicio=turno.fecha_hora_inicio,
        fin=fecha_hora_fin,
    )

    if hay_superposicion(
        db=db,
        id_negocio=turno.id_negocio,
        id_empleado=turno.id_empleado,
        inicio=turno.fecha_hora_inicio,
        fin=fecha_hora_fin,
    ):
        raise HTTPException(
            status_code=409,
            detail=SOLAPAMIENTO_DETALLE,
        )

    # Buscamos los datos del cliente para WhatsApp ANTES de crear el turno
    cliente = db.query(Cliente).filter(Cliente.id_cliente == turno.id_cliente).first()
    if not cliente:
        raise HTTPException(
            status_code=404,  # Cambiado a 404 estándar de HTTP para Not Found
            detail="El cliente especificado no existe."
        )

    ahora = datetime.now(UTC)
    id_estado_inicial = _resolver_estado_inicial(servicio)

    nuevo_turno = Turno(
        id_negocio=turno.id_negocio,
        id_cliente=turno.id_cliente,
        id_servicio=turno.id_servicio,
        id_estado=id_estado_inicial,
        id_empleado=turno.id_empleado,
        fecha_hora_inicio=turno.fecha_hora_inicio,
        fecha_hora_fin=fecha_hora_fin,
        rechazado_motivo=None,
        created_at=ahora,
        updated_at=ahora,
    )

    try:
        db.add(nuevo_turno)
        db.commit()
        db.refresh(nuevo_turno)

        # 🚀 INTEGRACIÓN DE TWILIO CON BACKGROUND TASKS 🚀
        try:
            # Formateamos fecha y hora como strings limpios antes de mandárselos a Twilio
            fecha_str = turno.fecha_hora_inicio.strftime("%d/%m/%Y")
            hora_str = turno.fecha_hora_inicio.strftime("%H:%M")
            nombre_completo = f"{cliente.nombre} {cliente.apellido}".strip()
            
            # Traemos el nombre del negocio mediante la relación del servicio
            nombre_negocio = servicio.negocio.nombre if hasattr(servicio, "negocio") else "TurnoGo"

            print(f"\n⏳ Encolando envío de WhatsApp en segundo plano para: {nombre_completo}")
            
            # Encolamos la tarea. FastAPI va a responder el HTTP 201 inmediatamente 
            # y en paralelo ejecutará esto sin trabar al usuario.
            background_tasks.add_task(
                telefono_cliente=cliente.telefono,
                nombre_cliente=nombre_completo,
                nombre_negocio=nombre_negocio,
                fecha=fecha_str,
                hora=hora_str
            )
            print("📦 Tarea registrada con éxito en BackgroundTasks.\n")

        except Exception as bg_error:
            # Si se rompe el formateo o la cola, lo capturamos para que NO rompa el commit exitoso del turno
            print(f"⚠️ Alerta: El turno se creó pero falló la cola de WhatsApp: {bg_error}")

        return nuevo_turno

    except IntegrityError as e:
        db.rollback()
        _lanzar_error_integridad(e)


def actualizar_turno(db: Session, turno_id: int, datos: TurnoActualizar):
    turno_db = db.query(Turno).filter(Turno.id_turno == turno_id).first()

    if not turno_db:
        raise HTTPException(status_code=404, detail="Turno no encontrado")

    nuevo_id_negocio = (
        datos.id_negocio if datos.id_negocio is not None else turno_db.id_negocio
    )
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

    servicio = obtener_servicio_del_negocio(
        db=db,
        id_servicio=nuevo_id_servicio,
        id_negocio=nuevo_id_negocio,
    )

    recalcular_fin = (
        datos.id_servicio is not None
        or datos.id_negocio is not None
        or datos.fecha_hora_inicio is not None
    )

    nueva_fecha_fin = (
        _resolver_fecha_hora_fin(
            db=db,
            id_servicio=nuevo_id_servicio,
            id_negocio=nuevo_id_negocio,
            fecha_hora_inicio=nueva_fecha_inicio,
            fecha_hora_fin=datos.fecha_hora_fin,
        )
        if recalcular_fin or datos.fecha_hora_fin is not None
        else turno_db.fecha_hora_fin
    )

    validar_rango_horario(nueva_fecha_inicio, nueva_fecha_fin)
    validar_empleado_del_negocio(
        db=db,
        id_negocio=nuevo_id_negocio,
        id_empleado=nuevo_id_empleado,
    )
    validar_turno_dentro_del_horario(
        db=db,
        id_negocio=nuevo_id_negocio,
        inicio=nueva_fecha_inicio,
        fin=nueva_fecha_fin,
    )
    if hay_superposicion(
        db=db,
        id_negocio=nuevo_id_negocio,
        id_empleado=nuevo_id_empleado,
        inicio=nueva_fecha_inicio,
        fin=nueva_fecha_fin,
        excluir_turno_id=turno_id,
    ):
        raise HTTPException(
            status_code=409,
            detail=SOLAPAMIENTO_DETALLE,
        )

    turno_db.id_negocio = nuevo_id_negocio
    turno_db.id_cliente = (
        datos.id_cliente if datos.id_cliente is not None else turno_db.id_cliente
    )
    turno_db.id_servicio = nuevo_id_servicio
    turno_db.id_empleado = nuevo_id_empleado
    turno_db.fecha_hora_inicio = nueva_fecha_inicio
    turno_db.fecha_hora_fin = nueva_fecha_fin

    if datos.id_estado is not None:
        turno_db.id_estado = datos.id_estado

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
            status_code=500, detail=f"Error al eliminar el turno: {str(e)}", )


def listar_turnos_por_negocio_y_rango(
    db: Session,
    id_negocio: int,
    desde: datetime,
    hasta: datetime,
    id_empleado: int | None = None,
):
    query = db.query(Turno).filter(
        Turno.id_negocio == id_negocio,
        Turno.fecha_hora_inicio < hasta,
        Turno.fecha_hora_fin > desde,
    )

    if id_empleado is not None:
        query = query.filter(Turno.id_empleado == id_empleado)

    return query.order_by(Turno.fecha_hora_inicio.asc()).all()
