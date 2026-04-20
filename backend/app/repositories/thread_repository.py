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
        self.db.commit()

    def get_owner(self, thread_id: str) -> str | None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT owner_user_id FROM thread_owners WHERE thread_id = %s
                """,
                (thread_id,)
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
                (thread_id, owner_user_id)
            )
        self.db.commit()