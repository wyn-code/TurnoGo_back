import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    from app.models.negocio import Negocio
    from app.models.cliente import Cliente
    from app.models.turnos import Turno
    from app.models.servicio import Servicio
    from app.models.usuario import Usuario
    from app.models.empleado import Empleado
    from app.models.provincia import Provincia
    from app.models.localidad import Localidad

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def seed_data(db):
    from app.models.negocio import Negocio
    from app.models.servicio import Servicio
    from app.models.empleado import Empleado
    from app.models.usuario import Usuario

    usuario_1 = Usuario(
        id_us=1,
        usuario_us="testuser1",
        email_us="test1@test.com",
        contrasena_us="123456"
    )
    usuario_2 = Usuario(
        id_us=2,
        usuario_us="testuser2",
        email_us="test2@test.com",
        contrasena_us="123456"
    )

    db.add_all([usuario_1, usuario_2])
    db.flush()

    negocio = Negocio(
        id_negocio=1,
        usuario_id=1,
        nombre="Test Negocio",
        rubro="Barberia",
        wsp="123456789",
        direccion="Test 123",
        ciudad="San Nicolas",
        activo=True,
        slug="test-negocio",
    )
    db.add(negocio)
    db.flush()

    servicio = Servicio(
        id_servicio=1,
        id_negocio=1,
        nombre_servicio="Corte",
        precio=1000,
        requiere_aprobacion=False,
        duracion_min=30,
        duracion_max=30,
        activo=True,
    )
    db.add(servicio)
    db.flush()

    empleado = Empleado(
        id_empleado=1,
        id_negocio=1,
        nombre="Juan",
        apellido="Perez",
        telefono="123456789",
        activo=True,
    )
    db.add(empleado)
    db.flush()

    return {
        "usuario_1": usuario_1,
        "usuario_2": usuario_2,
        "negocio": negocio,
        "servicio": servicio,
        "empleado": empleado,
    }