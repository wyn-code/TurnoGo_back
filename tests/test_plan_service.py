from datetime import datetime, timedelta
from app.services import plan_service
from app.models.plan import Plan
from app.models.plan_feature import PlanFeature
from app.models.suscripcion import Suscripcion


def _crear_plan_vip_con_features(db) -> Plan:
    plan = Plan(
        id_plan=1,
        nombre="VIP Mensual",
        precio=9999,
        duracion_dias=30,
        activo=True,
    )
    db.add(plan)
    db.flush()

    features = [
        PlanFeature(id_plan=plan.id_plan, feature_key="mapa_ubicacion"),
        PlanFeature(id_plan=plan.id_plan, feature_key="imagenes_personalizadas"),
        PlanFeature(id_plan=plan.id_plan, feature_key="soporte_prioritario"),
    ]
    db.add_all(features)
    db.commit()
    return plan


def test_negocio_con_suscripcion_activa_tiene_la_feature(db, seed_data):
    plan = _crear_plan_vip_con_features(db)
    negocio = seed_data["negocio"]

    suscripcion = Suscripcion(
        id_negocio=negocio.id_negocio,
        id_plan=plan.id_plan,
        estado="activa",
        fecha_inicio=datetime.now(),
        fecha_fin=datetime.now() + timedelta(days=30),
    )
    db.add(suscripcion)
    db.commit()

    assert plan_service.negocio_tiene_funcion(negocio.id_negocio, "mapa_ubicacion", db) is True


def test_negocio_sin_suscripcion_no_tiene_ninguna_feature(db, seed_data):
    _crear_plan_vip_con_features(db)
    negocio = seed_data["negocio"]

    assert plan_service.negocio_tiene_funcion(negocio.id_negocio, "mapa_ubicacion", db) is False
    assert plan_service.obtener_funciones_negocio(negocio.id_negocio, db) == []


def test_negocio_con_suscripcion_vencida_no_tiene_acceso(db, seed_data):
    plan = _crear_plan_vip_con_features(db)
    negocio = seed_data["negocio"]

    suscripcion = Suscripcion(
        id_negocio=negocio.id_negocio,
        id_plan=plan.id_plan,
        estado="activa",  # OJO: estado sigue "activa" pero la fecha ya venció
        fecha_inicio=datetime.now() - timedelta(days=60),
        fecha_fin=datetime.now() - timedelta(days=1),
    )
    db.add(suscripcion)
    db.commit()

    assert plan_service.negocio_tiene_funcion(negocio.id_negocio, "mapa_ubicacion", db) is False


def test_feature_inexistente_devuelve_false(db, seed_data):
    plan = _crear_plan_vip_con_features(db)
    negocio = seed_data["negocio"]

    suscripcion = Suscripcion(
        id_negocio=negocio.id_negocio,
        id_plan=plan.id_plan,
        estado="activa",
        fecha_inicio=datetime.now(),
        fecha_fin=datetime.now() + timedelta(days=30),
    )
    db.add(suscripcion)
    db.commit()

    assert plan_service.negocio_tiene_funcion(negocio.id_negocio, "feature_que_no_existe", db) is False


def test_obtener_funciones_negocio_devuelve_todas_las_del_plan(db, seed_data):
    plan = _crear_plan_vip_con_features(db)
    negocio = seed_data["negocio"]

    suscripcion = Suscripcion(
        id_negocio=negocio.id_negocio,
        id_plan=plan.id_plan,
        estado="activa",
        fecha_inicio=datetime.now(),
        fecha_fin=datetime.now() + timedelta(days=30),
    )
    db.add(suscripcion)
    db.commit()

    funciones = plan_service.obtener_funciones_negocio(negocio.id_negocio, db)
    assert set(funciones) == {"mapa_ubicacion", "imagenes_personalizadas", "soporte_prioritario"}


def test_obtener_suscripcion_activa_devuelve_el_plan_correcto(db, seed_data):
    plan = _crear_plan_vip_con_features(db)
    negocio = seed_data["negocio"]

    suscripcion = Suscripcion(
        id_negocio=negocio.id_negocio,
        id_plan=plan.id_plan,
        estado="activa",
        fecha_inicio=datetime.now(),
        fecha_fin=datetime.now() + timedelta(days=30),
    )
    db.add(suscripcion)
    db.commit()

    resultado = plan_service.obtener_suscripcion_activa(negocio.id_negocio, db)
    assert resultado is not None
    assert resultado.plan.nombre == "VIP Mensual"