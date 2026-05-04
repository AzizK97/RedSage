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
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    project_identifier TEXT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_thread_messages_thread_id
                ON thread_messages (thread_id, id)
                """
            )
            # Ensure search_tsv column exists for full-text search
            cur.execute("ALTER TABLE thread_messages ADD COLUMN IF NOT EXISTS search_tsv tsvector")
            # Create indexes used by search if missing
            cur.execute("CREATE INDEX IF NOT EXISTS idx_thread_messages_search_tsv ON thread_messages USING GIN(search_tsv)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_thread_messages_content_trgm ON thread_messages USING GIN (content gin_trgm_ops)")
        self.db.commit()

    def append(self, thread_id: str, role: str, content: str) -> None:
        with self.db.cursor() as cur:
            # Attempt to copy project_identifier from thread_owners so messages are searchable by project
            cur.execute("SELECT project_identifier FROM thread_owners WHERE thread_id = %s", (thread_id,))
            proj_row = cur.fetchone()
            proj_identifier = proj_row[0] if proj_row else None

            cur.execute(
                """
                INSERT INTO thread_messages (thread_id, role, content, project_identifier)
                VALUES (%s, %s, %s, %s)
                """,
                (thread_id, role, content, proj_identifier),
            )
        self.db.commit()

    def search_messages(self, query: str, allowed_project_identifiers: list | None = None, limit: int = 50, offset: int = 0) -> dict:
        """Search messages using Postgres full-text search with optional project filtering.

        Returns dict with keys: items (list) and total (int).
        """
        if allowed_project_identifiers is not None and len(allowed_project_identifiers) == 0:
            return {"total": 0, "items": []}

        with self.db.cursor() as cur:
            # Count
            if allowed_project_identifiers is None:
                cur.execute(
                    "SELECT COUNT(*) FROM thread_messages WHERE search_tsv @@ plainto_tsquery('english', %s)",
                    (query,),
                )
            else:
                cur.execute(
                    "SELECT COUNT(*) FROM thread_messages WHERE search_tsv @@ plainto_tsquery('english', %s) AND project_identifier = ANY(%s::text[])",
                    (query, allowed_project_identifiers),
                )
            total = cur.fetchone()[0]

            # Rows
            if allowed_project_identifiers is None:
                cur.execute(
                    """
                    SELECT id, thread_id, role, content, created_at, ts_rank_cd(search_tsv, plainto_tsquery('english', %s)) AS rank
                    FROM thread_messages
                    WHERE search_tsv @@ plainto_tsquery('english', %s)
                    ORDER BY rank DESC, created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (query, query, limit, offset),
                )
            else:
                cur.execute(
                    """
                    SELECT id, thread_id, role, content, created_at, ts_rank_cd(search_tsv, plainto_tsquery('english', %s)) AS rank
                    FROM thread_messages
                    WHERE search_tsv @@ plainto_tsquery('english', %s)
                      AND project_identifier = ANY(%s::text[])
                    ORDER BY rank DESC, created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (query, query, allowed_project_identifiers, limit, offset),
                )
            rows = cur.fetchall()

        items = [
            {
                "id": r[0],
                "thread_id": r[1],
                "role": r[2],
                "content": r[3],
                "created_at": r[4].isoformat() if r[4] else None,
                "rank": float(r[5]) if r[5] is not None else 0.0,
            }
            for r in rows
        ]

        return {"total": total, "items": items}

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
