import os
import pytest
import psycopg
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies.db import get_db, get_agent_db
from app.dependencies.auth import get_current_user
from app.core.security import create_access_token
from app.models.user import RedmineUser

# Point this at a DEDICATED throwaway database; its tables are truncated between
# tests. The schema is created automatically, but the database must have the
# pg_trgm extension (CREATE EXTENSION pg_trgm;).
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/redmine_chat_test",
)

# Application-owned tables, children before parents, truncated between tests.
_APP_TABLES = [
    "thread_messages",
    "thread_owners",
    "entitlements",
    "redmine_users",
]

# ==================== DATABASE FIXTURES ====================


def _ensure_app_tables(conn):
    from app.repositories.user_repository import UserRepository
    from app.repositories.entitlement_repository import EntitlementRepository
    from app.repositories.thread_repository import ThreadRepository
    from app.repositories.thread_message_repository import ThreadMessageRepository

    UserRepository(conn).ensure_table()
    EntitlementRepository(conn).ensure_table()
    ThreadRepository(conn).ensure_table()
    ThreadMessageRepository(conn).ensure_table()


def _truncate_app_tables(conn):
    with conn.cursor() as cur:
        for table in _APP_TABLES:
            try:
                cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
            except Exception:
                # Table may not exist yet; with autocommit there is no aborted
                # transaction to recover from, so ignore and continue.
                pass


@pytest.fixture(scope="function")
def test_db_connection():
    """Real connection to the test database, cleaned between tests.

    Uses autocommit: the repositories commit internally, which psycopg forbids
    inside an explicit transaction block, so per-test isolation is achieved by
    truncating the application tables rather than by rolling a transaction back.
    """
    conn = psycopg.connect(TEST_DATABASE_URL, autocommit=True)
    try:
        _ensure_app_tables(conn)
        _truncate_app_tables(conn)
        yield conn
    finally:
        try:
            _truncate_app_tables(conn)
        finally:
            conn.close()


def get_test_db_override(conn):
    """Dependency override for FastAPI: yield the shared test connection."""
    def _get_db():
        yield conn
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
    app.dependency_overrides[get_agent_db] = get_test_db_override(test_db_connection)
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
    app.dependency_overrides[get_agent_db] = get_test_db_override(test_db_connection)
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