from psycopg import Connection


class EntitlementRepository:
    def __init__(self, db: Connection) -> None:
        self.db = db

    def ensure_table(self) -> None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS entitlements (
                    user_id TEXT PRIMARY KEY REFERENCES redmine_users(id) ON DELETE CASCADE,
                    enabled BOOLEAN NOT NULL DEFAULT FALSE,
                    enabled_by_admin_id TEXT NULL,
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
        self.db.commit()

    def is_enabled(self, user_id: str) -> bool:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT enabled
                FROM entitlements
                WHERE user_id = %s
                """,
                (user_id,),
            )
            row = cur.fetchone()

        return bool(row[0]) if row else False
    
    def set_access(self, user_id:str, enabled:bool, admin_user_id:str) -> None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO entitlements (user_id, enabled, enabled_by_admin_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id)
                DO UPDATE SET enabled = EXCLUDED.enabled,
                              enabled_by_admin_id = EXCLUDED.enabled_by_admin_id,
                              updated_at = NOW()
                """,
                (user_id, enabled, admin_user_id)
            )
        self.db.commit()