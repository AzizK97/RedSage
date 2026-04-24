import uuid
from psycopg import Connection


class UserRepository:
    def __init__(self, db: Connection) -> None:
        self.db = db

    def ensure_table(self) -> None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS redmine_users (
                    id TEXT PRIMARY KEY,
                    redmine_user_id INTEGER UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    platform_role TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
        self.db.commit()

    def get_by_redmine_user_id(self, redmine_user_id: int) -> dict | None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT id, redmine_user_id, email, full_name, platform_role
                FROM redmine_users
                WHERE redmine_user_id = %s
                """,
                (redmine_user_id,),
            )
            row = cur.fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "redmine_user_id": row[1],
            "email": row[2],
            "full_name": row[3],
            "platform_role": row[4],
        }

    def list_by_role(self, platform_role: str) -> list[dict]:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT id, redmine_user_id, email, full_name, platform_role
                FROM redmine_users
                WHERE platform_role = %s
                ORDER BY full_name ASC
                """,
                (platform_role,),
            )
            rows = cur.fetchall()

        return [
            {
                "id": row[0],
                "redmine_user_id": row[1],
                "email": row[2],
                "full_name": row[3],
                "platform_role": row[4],
            }
            for row in rows
        ]

    def mirror_user_from_redmine(
            self,
            redmine_user_id: int,
            email: str,
            full_name: str,
            platform_role: str = "member",
    ) -> dict: 
        existing = self.get_by_redmine_user_id(redmine_user_id)

        if existing:
            with self.db.cursor() as cur:
                cur.execute(
                    """
                    UPDATE redmine_users
                    SET email = %s, full_name = %s, platform_role = %s
                    WHERE redmine_user_id = %s
                    """,
                    (email, full_name, platform_role, redmine_user_id),
                )
            self.db.commit()
            return self.get_by_redmine_user_id(redmine_user_id)
        
        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO redmine_users (id, redmine_user_id, email, full_name, platform_role)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (str(uuid.uuid4()), redmine_user_id, email, full_name, platform_role),
            )
        self.db.commit()
        return self.get_by_redmine_user_id(redmine_user_id)
