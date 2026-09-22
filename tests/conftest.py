import os
import sys
from pathlib import Path

# Configurar variables de entorno para tests ANTES de importar cualquier módulo
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("TESTING", "true")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing")
os.environ.setdefault("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("DATA_DIR", "./test_data")
os.environ.setdefault("PORT", "8080")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importar después de configurar variables de entorno
from app.main import app
from app.database import Base, get_db
from app.models import Usuario, UserRole, Condominio, Propiedad
from app.security import hash_password

# Engine de base de datos para tests (override el engine de app.database)
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Monkey patch del engine en app.database para tests
import app.database as db_module
db_module.engine = engine
db_module.SessionLocal = TestingSessionLocal


@pytest.fixture(scope="function")
def db_session():
    """Fixture para crear una sesión de base de datos para tests."""
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Fixture para crear un cliente de测试 con base de datos limpia."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Fixture para crear un usuario de prueba."""
    # Crear condominio y propiedad
    condominio = Condominio(
        nombre="Condominio Test",
        direccion="Dirección Test"
    )
    db_session.add(condominio)
    db_session.flush()
    
    propiedad = Propiedad(
        condominio_id=condominio.id,
        numero_unidad="TEST-01",
        es_solvente=True
    )
    db_session.add(propiedad)
    db_session.flush()
    
    # Crear usuario ADMIN_CASA
    user = Usuario(
        propiedad_id=propiedad.id,
        nombre="Usuario Test",
        email="test@example.com",
        cedula="V-12345678",
        password_hash=hash_password("TestPassword123!"),
        rol=UserRole.ADMIN_CASA
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def test_vigilante(db_session):
    """Fixture para crear un usuario vigilante de prueba."""
    user = Usuario(
        propiedad_id=None,
        nombre="Vigilante Test",
        email="vigilante@example.com",
        cedula="V-87654321",
        password_hash=hash_password("TestPassword123!"),
        rol=UserRole.VIGILANTE
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Fixture para obtener headers de autenticación."""
    response = client.post("/auth/login", data={
        "username": test_user.email,
        "password": "TestPassword123!"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def vigilante_headers(client, test_vigilante):
    """Fixture para obtener headers de autenticación de vigilante."""
    response = client.post("/auth/login", data={
        "username": test_vigilante.email,
        "password": "TestPassword123!"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
