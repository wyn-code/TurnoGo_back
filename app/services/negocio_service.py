import re
import unicodedata
from app.models.usuario import Usuario
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.negocio import Negocio
from app.models.servicio import Servicio
from app.models.empleado import Empleado
from app.schemas.negocio_schema import NegocioCreate, NegocioCompleteCreate


def listar_negocios(db: Session):
    return db.query(Negocio).all()

def listar_negocios_admin(db: Session):
    resultados = (
        db.query(Negocio, Usuario)
        .join(Usuario, Negocio.usuario_id == Usuario.id_us)
        .all()
    )

    negocios = []

    for negocio, usuario in resultados:
        negocios.append({
            "id_negocio": negocio.id_negocio,
            "nombre": negocio.nombre,
            "rubro": negocio.rubro,
            "slug": negocio.slug,
            "activo": negocio.activo,
            "duenio": {
                "nombre": usuario.usuario_us,
                "email": usuario.email_us
            }
        })

    return negocios


def obtener_negocio_por_id(db: Session, negocio_id: int):
    negocio = db.query(Negocio).filter(Negocio.id_negocio == negocio_id).first()
    if not negocio:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return negocio


def obtener_negocio_por_slug(db: Session, slug: str):
    negocio = db.query(Negocio).filter(Negocio.slug == slug).first()
    if not negocio:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return negocio


def slugify(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode(
        "ascii", "ignore"
    ).decode("ascii")
    texto = texto.lower().strip()
    texto = re.sub(r"[^a-z0-9\s-]", "", texto)
    texto = re.sub(r"[\s-]+", "-", texto)
    return texto

def generar_slug(nombre: str) -> str:
    slug = nombre.lower()
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    return slug


def generar_slug_unico(db, nombre: str):
    base_slug = generar_slug(nombre)
    slug = base_slug
    contador = 1

    while db.query(Negocio).filter(Negocio.slug == slug).first():
        slug = f"{base_slug}-{contador}"
        contador += 1

    return slug


def crear_negocio(db: Session, data: NegocioCreate):
    # 🔥 Validaciones
    if data.id_categoria is None:
        raise HTTPException(status_code=400, detail="id_categoria es obligatorio")

    if data.usuario_id is None:
        raise HTTPException(status_code=400, detail="usuario_id es obligatorio")

    # 🔥 Slug único (mejor que el simple)
    slug = generar_slug_unico(db, data.nombre)

    nuevo_negocio = Negocio(
        usuario_id=data.usuario_id,
        nombre=data.nombre,
        rubro=data.rubro,
        wsp=data.wsp,
        telefono=data.telefono,
        direccion=data.direccion,
        ciudad=data.ciudad,
        id_localidad=data.id_localidad,
        id_provincia=data.id_provincia,
        ig_url=data.ig_url,
        logo=data.logo,
        activo=data.activo,
        id_categoria=data.id_categoria,
        slug=slug,
    )

    try:
        db.add(nuevo_negocio)
        db.commit()
        db.refresh(nuevo_negocio)
        return nuevo_negocio

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error de integridad al crear negocio: {str(e.orig)}",
        ) from e

def crear_negocio_completo(db: Session, data: NegocioCompleteCreate):
    slug = generar_slug_unico(db, data.nombre)

    nuevo_negocio = Negocio(
        usuario_id=data.usuario_id,
        nombre=data.nombre,
        rubro=data.rubro,
        wsp=data.wsp,
        telefono=data.telefono,
        direccion=data.direccion,
        ciudad=data.ciudad,
        id_localidad=data.id_localidad,
        id_provincia=data.id_provincia,
        ig_url=data.ig_url,
        logo=data.logo,
        activo=data.activo,
        slug=slug,
    )

    try:
        db.add(nuevo_negocio)
        db.flush()

        for servicio in data.servicios:
            nuevo_servicio = Servicio(
                id_negocio=nuevo_negocio.id_negocio,
                nombre_servicio=servicio.nombre_servicio,
                precio=servicio.precio,
                requiere_aprobacion=servicio.requiere_aprobacion,
                duracion_min=servicio.duracion_min,
                duracion_max=servicio.duracion_max,
                activo=servicio.activo,
            )
            db.add(nuevo_servicio)

        for empleado in data.empleados:
            nuevo_empleado = Empleado(
                id_negocio=nuevo_negocio.id_negocio,
                nombre=empleado.nombre,
                apellido=empleado.apellido,
                telefono=empleado.telefono,
                activo=empleado.activo,
            )
            db.add(nuevo_empleado)

        db.commit()
        db.refresh(nuevo_negocio)
        return nuevo_negocio

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error de integridad al crear negocio completo: {str(e.orig)}",
        ) from e

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear negocio completo: {str(e)}",
        ) from e