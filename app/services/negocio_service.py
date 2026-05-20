import re
import unicodedata
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models.negocio import Negocio
from app.models.usuario import Usuario
from app.models.servicio import Servicio
from app.models.empleado import Empleado
from app.models.categoria import Categoria

from app.schemas.negocio_schema import NegocioCreate, NegocioCompleteCreate


def listar_negocios(db: Session):
    return db.query(Negocio).filter(
        Negocio.activo == True
    ).all()


def listar_negocios_admin(db: Session):
    resultados = (
        db.query(Negocio, Usuario)
        .options(joinedload(Negocio.categoria))
        .join(
            Usuario,
            Negocio.usuario_id == Usuario.id_us
        )
        .all()
    )

    negocios = []

    for negocio, usuario in resultados:
        negocios.append({
            "id_negocio": negocio.id_negocio,
            "nombre": negocio.nombre,

            "wsp": negocio.wsp,
            "telefono": negocio.telefono,
            "direccion": negocio.direccion,
            "ciudad": negocio.ciudad,
            "ig_url": negocio.ig_url,

            "categoria":
                negocio.categoria.nombre
                if negocio.categoria
                else None,

            "slug": negocio.slug,
            "activo": negocio.activo,

            "duenio": {
                "nombre": usuario.usuario_us,
                "email": usuario.email_us,
            },
        })

    return negocios

def obtener_negocio_por_id(db: Session, negocio_id: int):
    negocio = db.query(Negocio).options(
        joinedload(Negocio.categoria)
    ).filter(
        Negocio.id_negocio == negocio_id
    ).first()

    if not negocio:
        raise HTTPException(
            status_code=404,
            detail="Negocio no encontrado"
        )

    return negocio

def obtener_negocio_publico_por_id(
    db: Session,
    negocio_id: int
):
    negocio = db.query(Negocio).options(
        joinedload(Negocio.categoria)
    ).filter(
        Negocio.id_negocio == negocio_id,
        Negocio.activo == True
    ).first()

    if not negocio:
        raise HTTPException(
            status_code=404,
            detail="Negocio no encontrado"
        )

    return negocio


def obtener_negocio_por_slug(db: Session, slug: str):
    negocio = db.query(Negocio).options(
        joinedload(Negocio.categoria)
    ).filter(
        Negocio.slug == slug,
        Negocio.activo == True
    ).first()

    if not negocio:
        raise HTTPException(
            status_code=404,
            detail="Negocio no encontrado"
        )

    return negocio


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


# ==============================
# 🔥 CREAR NEGOCIO SIMPLE
# ==============================
def crear_negocio(db: Session, data: NegocioCreate):

    if data.usuario_id is None:
        raise HTTPException(
            status_code=400, detail="usuario_id es obligatorio")

    if data.id_categoria is None:
        raise HTTPException(
            status_code=400, detail="id_categoria es obligatorio")

    # 🔥 Obtener categoría
    categoria = db.query(Categoria).filter(
        Categoria.id_categoria == data.id_categoria
    ).first()

    if not categoria:
        raise HTTPException(status_code=400, detail="Categoría no válida")

    slug = generar_slug_unico(db, data.nombre)

    nuevo_negocio = Negocio(
        usuario_id=data.usuario_id,
        nombre=data.nombre,
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
        )


# ==============================
# 🔥 CREAR NEGOCIO COMPLETO
# ==============================
def crear_negocio_completo(db: Session, data: NegocioCompleteCreate):

    if data.usuario_id is None:
        raise HTTPException(
            status_code=400, detail="usuario_id es obligatorio")

    if data.id_categoria is None:
        raise HTTPException(
            status_code=400, detail="id_categoria es obligatorio")

    # 🔥 Obtener categoría
    categoria = db.query(Categoria).filter(
        Categoria.id_categoria == data.id_categoria
    ).first()

    if not categoria:
        raise HTTPException(status_code=400, detail="Categoría no válida")

    # ❌ ELIMINAMOS LA VARIABLE rubro = categoria.nombre (ya no se usa)

    slug = generar_slug_unico(db, data.nombre)

    nuevo_negocio = Negocio(
        usuario_id=data.usuario_id,
        nombre=data.nombre,
        # ✅ ELIMINADA la línea rubro=rubro
        wsp=data.wsp,
        telefono=data.telefono,
        direccion=data.direccion,
        ciudad=data.ciudad,
        id_localidad=data.id_localidad,
        id_provincia=data.id_provincia,
        ig_url=data.ig_url,
        logo=data.logo,
        activo=data.activo,
        id_categoria=data.id_categoria,  # 👈 Esto es lo que importa ahora
        slug=slug,
    )

    try:
        db.add(nuevo_negocio)
        db.flush()  # 🔥 obtiene id_negocio sin commit

        # 🔥 Servicios
        for servicio in data.servicios:
            nuevo_servicio = Servicio(
                nombre_servicio=servicio.nombre_servicio,
                precio=servicio.precio,
                requiere_aprobacion=servicio.requiere_aprobacion,
                duracion_min=servicio.duracion_min,
                duracion_max=servicio.duracion_max,
                activo=servicio.activo,
                id_negocio=nuevo_negocio.id_negocio 
            )
            db.add(nuevo_servicio)

        # 🔥 Empleados
        for empleado in data.empleados:
            nuevo_empleado = Empleado(
                nombre=empleado.nombre,
                apellido=empleado.apellido,
                telefono=empleado.telefono,
                activo=empleado.activo,
                id_negocio=nuevo_negocio.id_negocio 
            )
            db.add(nuevo_empleado)

        db.commit()
        db.refresh(nuevo_negocio)
        return nuevo_negocio

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
