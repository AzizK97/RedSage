import os
import pytest
import psycopg
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.core.security import create_access_token
from app.models.user import RedmineUser

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "postgresql+psycopg://localhost/redmine_chat_test"
)

# ==================== DATABASE FIXTURES ====================

@pytest.fixture(scope="function")
def test_db_connection():
    """Create a real DB connection with transaction rollback per test."""
    conn = psycopg.connect(TEST_DATABASE_URL, autocommit=False)
    try:
        with conn.transaction():
            yield conn
            # If no exception, we rollback at the end of the 'with' block
    finally:
        conn.close()


def get_test_db_override(conn):
    """Dependency override for FastAPI."""
    def _get_db():
        try:
            yield conn
        finally:
            pass  # Connection will be cleaned by the transaction context
    return _get_db


# ==================== USER & AUTH FIXTURES ====================

@pytest.fixture(scope="function")
def test_user():
    return RedmineUser(
        id=1,
        redmine_user_id=123,
        email="test@example.com",
        full_name="Test User",
        role="project_manager",
    )


@pytest.fixture
def test_token(test_user):
    return create_access_token(
        data={
            "sub": str(test_user.redmine_user_id),
            "redmine_user_id": test_user.redmine_user_id,
            "email": test_user.email,
            "role": test_user.role,
        },
        expires_minutes=60 * 24
    )


def get_test_user_override(test_user):
    async def _get_current_user():
        return test_user
    return _get_current_user


# ==================== CLIENT FIXTURES ====================

@pytest.fixture
async def async_client(test_db_connection, test_user):
    """Async client with dependency overrides."""
    app.dependency_overrides[get_db] = get_test_db_override(test_db_connection)
    app.dependency_overrides[get_current_user] = get_test_user_override(test_user)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def sync_client(test_db_connection, test_user):
    """Synchronous TestClient (useful for simpler tests)."""
    app.dependency_overrides[get_db] = get_test_db_override(test_db_connection)
    app.dependency_overrides[get_current_user] = get_test_user_override(test_user)

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


# ==================== AUTHENTICATED CLIENTS ====================

@pytest.fixture
async def authenticated_async_client(async_client, test_token):
    async_client.headers["Authorization"] = f"Bearer {test_token}"
    return async_client


@pytest.fixture
def authenticated_sync_client(sync_client, test_token):
    sync_client.headers["Authorization"] = f"Bearer {test_token}"
    return sync_client