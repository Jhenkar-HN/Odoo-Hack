import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.core.database import Base, get_db
from backend.app.utils.seeder import seed_database

import os

# Dynamic test database URL (supports MySQL test instance or isolated in-memory)
TEST_DB_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")

test_engine_kwargs = {}
if TEST_DB_URL.startswith("sqlite"):
    test_engine_kwargs = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
else:
    test_engine_kwargs = {
        "pool_pre_ping": True,
    }

engine = create_engine(TEST_DB_URL, **test_engine_kwargs)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh in-memory database and seed it for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        seed_database(db)
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Override get_db dependency and yield TestClient."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client: TestClient) -> str:
    """Obtain JWT token for Admin."""
    res = client.post("/api/v1/auth/login", json={"login_id": "admin@hrmscorp.com", "password": "Admin@123"})
    assert res.status_code == 200
    return res.json()["data"]["access_token"]


@pytest.fixture
def hr_token(client: TestClient) -> str:
    """Obtain JWT token for HR Officer."""
    res = client.post("/api/v1/auth/login", json={"login_id": "hr@hrmscorp.com", "password": "Hr@123"})
    assert res.status_code == 200
    return res.json()["data"]["access_token"]


@pytest.fixture
def employee_token(client: TestClient) -> str:
    """Obtain JWT token for standard Employee (John Doe)."""
    res = client.post("/api/v1/auth/login", json={"login_id": "john.doe@hrmscorp.com", "password": "Emp@123"})
    assert res.status_code == 200
    return res.json()["data"]["access_token"]


@pytest.fixture
def employee2_token(client: TestClient) -> str:
    """Obtain JWT token for second Employee (Alice Smith)."""
    res = client.post("/api/v1/auth/login", json={"login_id": "alice.smith@hrmscorp.com", "password": "Emp@123"})
    assert res.status_code == 200
    return res.json()["data"]["access_token"]
