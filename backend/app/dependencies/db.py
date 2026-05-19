from collections.abc import Generator
import os
import psycopg
from app.core.config import settings


def get_db() -> Generator[psycopg.Connection, None, None]:
    """Dependency that yields a connection to the platform Postgres DB.

    Uses `PLATFORM_POSTGRES_URL` from settings.
    """
    if not settings.PLATFORM_POSTGRES_URL:
        raise RuntimeError("PLATFORM_POSTGRES_URL is not configured")
    conn = psycopg.connect(settings.PLATFORM_POSTGRES_URL)
    try:
        yield conn
    finally:
        conn.close()


def get_agent_db() -> Generator[psycopg.Connection, None, None]:
    """Dependency that yields a connection to the agent Postgres DB.

    This reads `POSTGRES_URL` from the environment which is used by the
    agent checkpointer and where durable chat/thread tables should live
    when you split databases.
    """
    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        raise RuntimeError("POSTGRES_URL is not configured")
    conn = psycopg.connect(postgres_url)
    try:
        yield conn
    finally:
        conn.close()