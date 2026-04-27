from collections.abc import Generator
import psycopg
from app.core.settings import settings

def get_db() -> Generator[psycopg.Connection, None, None]:
    if not settings.PLATFORM_POSTGRES_URL:
        raise RuntimeError("PLATFORM_POSTGRES_URL is not configured")
    conn = psycopg.connect(settings.PLATFORM_POSTGRES_URL)
    try:
        yield conn
    finally:
        conn.close()