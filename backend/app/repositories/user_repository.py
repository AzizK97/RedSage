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
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    platform_role TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
        self.db.commit()

    def get_by_email(self, email: str) -> dict | None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT id, redmine_user_id, email, password_hash, full_name, platform_role
                FROM redmine_users
                WHERE email = %s
                """,
                (email,),
            )
            row = cur.fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "redmine_user_id": row[1],
            "email": row[2],
            "password_hash": row[3],
            "full_name": row[4],
            "platform_role": row[5],
        }

    def get_by_redmine_user_id(self, redmine_user_id: int) -> dict | None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT id, redmine_user_id, email, password_hash, full_name, platform_role
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
            "password_hash": row[3],
            "full_name": row[4],
            "platform_role": row[5],
        }

    def create_user(
            self,
            redmine_user_id: int,
            email: str,
            password_hash: str,
            full_name: str,
            platform_role: str,
    ) -> dict:
        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO redmine_users (id, redmine_user_id, email, password_hash, full_name, platform_role)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, redmine_user_id, email, full_name, platform_role
                """,
                (str(uuid.uuid4()), redmine_user_id, email, password_hash, full_name, platform_role),
            )
            row = cur.fetchone()
        self.db.commit()

        return{
            "id": row[0],
            "redmine_user_id": row[1],
            "email": row[2],
            "full_name": row[3],
            "platform_role": row[4],
        }

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
                INSERT INTO redmine_users (id, redmine_user_id, email, password_hash, full_name, platform_role)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (str(uuid.uuid4()), redmine_user_id, email, "", full_name, platform_role),
            )
        self.db.commit()
        return self.get_by_redmine_user_id(redmine_user_id)

    def update_password_hash(self, user_id: str, password_hash: str) -> None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                UPDATE redmine_users
                SET password_hash = %s
                WHERE id = %s
                """,
                (password_hash, user_id),
            )
        self.db.commit()

    def list_project_managers_with_access(self) -> list[dict]:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT
                    u.id,
                    u.redmine_user_id,
                    u.email,
                    u.full_name,
                    CASE WHEN COALESCE(BTRIM(u.password_hash), '') <> '' THEN TRUE ELSE FALSE END AS credentials_ready,
                    COALESCE(e.enabled, FALSE) AS enabled
                FROM redmine_users u
                LEFT JOIN entitlements e ON e.user_id = u.id
                WHERE u.platform_role = 'project_manager'
                ORDER BY u.full_name ASC, u.redmine_user_id ASC
                """
            )
            rows = cur.fetchall()

        return [
            {
                "user_id": row[0],
                "redmine_user_id": row[1],
                "email": row[2],
                "full_name": row[3],
                "in_platform": True,
                "credentials_ready": bool(row[4]),
                "enabled": bool(row[5]),
            }
            for row in rows
        ]
