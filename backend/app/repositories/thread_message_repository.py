import time
from psycopg import Connection


class ThreadMessageRepository:
    def __init__(self, db: Connection) -> None:
        self.db = db

    def ensure_table(self) -> None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS thread_messages (
                    id BIGSERIAL PRIMARY KEY,
                    thread_id TEXT NOT NULL REFERENCES thread_owners (thread_id) ON DELETE CASCADE,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_thread_messages_thread_id
                ON thread_messages (thread_id, id)
                """
            )
        self.db.commit()

    def append(self, thread_id: str, role: str, content: str) -> None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO thread_messages (thread_id, role, content)
                VALUES (%s, %s, %s)
                """,
                (thread_id, role, content),
            )
        self.db.commit()

    def list_for_thread(self, thread_id: str) -> list[dict]:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT role, content, EXTRACT(EPOCH FROM created_at) * 1000 AS ts_ms
                FROM thread_messages
                WHERE thread_id = %s
                ORDER BY id ASC
                """,
                (thread_id,),
            )
            rows = cur.fetchall()
        return [
            {
                "role": r[0],
                "content": r[1],
                "timestamp": int(r[2]) if r[2] is not None else int(time.time() * 1000),
            }
            for r in rows
        ]

    def delete_for_thread(self, thread_id: str) -> None:
        with self.db.cursor() as cur:
            cur.execute("DELETE FROM thread_messages WHERE thread_id = %s", (thread_id,))
        self.db.commit()
