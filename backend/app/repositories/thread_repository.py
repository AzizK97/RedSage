import uuid

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
                    title TEXT NOT NULL DEFAULT 'New conversation',
                    preview TEXT NOT NULL DEFAULT 'No messages yet',
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
            cur.execute("ALTER TABLE thread_owners ADD COLUMN IF NOT EXISTS title TEXT NOT NULL DEFAULT 'New conversation'")
            cur.execute("ALTER TABLE thread_owners ADD COLUMN IF NOT EXISTS preview TEXT NOT NULL DEFAULT 'No messages yet'")
            cur.execute("ALTER TABLE thread_owners ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW()")
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
    
    def create_thread(self, owner_user_id: str, title: str = 'New conversation') -> str:
        thread_id = str(uuid.uuid4())
        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO thread_owners (thread_id, owner_user_id, title, preview)
                VALUES (%s, %s, %s, %s)
                """,
                (thread_id, owner_user_id, title, 'No messages yet')
            )
        self.db.commit()
        return thread_id

    def list_threads_for_owner(self, owner_user_id: str) -> list[dict]:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT thread_id, title, preview, updated_at
                FROM thread_owners
                WHERE owner_user_id = %s
                ORDER BY updated_at DESC, created_at DESC
                """,
                (owner_user_id,)
            )
            rows = cur.fetchall()

        return [
            {
                "id": row[0],
                "title": row[1],
                "preview": row[2],
                "updatedAt": row[3].timestamp() * 1000 if row[3] else 0,
            }
            for row in rows
        ]

    def update_thread_summary(self, thread_id: str, title: str, preview: str) -> None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                UPDATE thread_owners
                SET title = %s,
                    preview = %s,
                    updated_at = NOW()
                WHERE thread_id = %s
                """,
                (title, preview, thread_id),
            )
        self.db.commit()

    def delete_thread(self, thread_id: str) -> None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                DELETE FROM thread_owners
                WHERE thread_id = %s
                """,
                (thread_id,),
            )
        self.db.commit()