import time
import uuid
from datetime import datetime, timezone
from psycopg import Connection


class ThreadRepository:
    def __init__(self, db: Connection) -> None:
        self.db = db

    def ensure_table(self) -> None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS thread_owners (
                    thread_id TEXT PRIMARY KEY,
                    owner_user_id TEXT NOT NULL REFERENCES redmine_users(id) ON DELETE CASCADE,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
            cur.execute(
                "ALTER TABLE thread_owners ADD COLUMN IF NOT EXISTS title TEXT NOT NULL DEFAULT 'New conversation'"
            )
            cur.execute(
                "ALTER TABLE thread_owners ADD COLUMN IF NOT EXISTS preview TEXT NOT NULL DEFAULT 'No messages yet'"
            )
            cur.execute(
                "ALTER TABLE thread_owners ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW()"
            )
        self.db.commit()

    def get_owner(self, thread_id: str) -> str | None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT owner_user_id FROM thread_owners WHERE thread_id = %s
                """,
                (thread_id,),
            )
            row = cur.fetchone()
        return row[0] if row else None

    def bind_owner_if_missing(self, thread_id: str, owner_user_id: str) -> None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO thread_owners (thread_id, owner_user_id)
                VALUES (%s, %s)
                ON CONFLICT (thread_id) DO NOTHING
                """,
                (thread_id, owner_user_id),
            )
        self.db.commit()

    def create_thread(self, owner_user_id: str) -> str:
        thread_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO thread_owners (thread_id, owner_user_id, title, preview, updated_at)
                VALUES (%s, %s, 'New conversation', 'No messages yet', %s)
                """,
                (thread_id, owner_user_id, now),
            )
        self.db.commit()
        return thread_id

    def list_for_owner(self, owner_user_id: str) -> list[dict]:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT thread_id, title, preview, updated_at, created_at
                FROM thread_owners
                WHERE owner_user_id = %s
                ORDER BY updated_at DESC
                """,
                (owner_user_id,),
            )
            rows = cur.fetchall()
        out = []
        for row in rows:
            updated = row[3] or row[4]
            ts_ms = int(updated.timestamp() * 1000) if updated else int(time.time() * 1000)
            out.append(
                {
                    "thread_id": row[0],
                    "title": row[1],
                    "preview": row[2],
                    "updated_at_ms": ts_ms,
                }
            )
        return out

    def update_metadata(self, thread_id: str, title: str, preview: str) -> None:
        now = datetime.now(timezone.utc)
        with self.db.cursor() as cur:
            cur.execute(
                """
                UPDATE thread_owners
                SET title = %s, preview = %s, updated_at = %s
                WHERE thread_id = %s
                """,
                (title, preview, now, thread_id),
            )
        self.db.commit()

    def update_preview(self, thread_id: str, preview: str) -> None:
        now = datetime.now(timezone.utc)
        with self.db.cursor() as cur:
            cur.execute(
                """
                UPDATE thread_owners
                SET preview = %s, updated_at = %s
                WHERE thread_id = %s
                """,
                (preview, now, thread_id),
            )
        self.db.commit()

    def delete_thread(self, thread_id: str) -> None:
        with self.db.cursor() as cur:
            cur.execute("DELETE FROM thread_owners WHERE thread_id = %s", (thread_id,))
        self.db.commit()
