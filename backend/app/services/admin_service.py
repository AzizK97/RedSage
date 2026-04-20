import secrets
import string

from psycopg import Connection
from app.core.security import hash_password
from app.integrations.redmine_client import redmine_client
from app.repositories.user_repository import UserRepository
from app.repositories.entitlement_repository import EntitlementRepository


class AdminService:
    def __init__(self, db: Connection) -> None:
        self.users = UserRepository(db)
        self.entitlements = EntitlementRepository(db)

    def set_pm_access(self, admin_user_id: str, redmine_user_id: int, enabled: bool) -> dict:

        user = self.users.get_by_redmine_user_id(redmine_user_id)

        generated_password = None

        if enabled:
            if not user:
                redmine_user = redmine_client.get_user(redmine_user_id)
                if not redmine_user:
                    raise ValueError("Redmine user not found.")

                email = redmine_user.get("mail", f"user{redmine_user_id}@example.com")
                full_name = (
                    f"{redmine_user.get('firstname', '')} {redmine_user.get('lastname', '')}".strip()
                    or redmine_user.get("login", "")
                    or f"User {redmine_user_id}"
                )

                user = self.users.mirror_user_from_redmine(
                    redmine_user_id=redmine_user_id,
                    email=email,
                    full_name=full_name,
                    platform_role="project_manager",
                )

            if user["platform_role"] != "project_manager":
                user = self.users.mirror_user_from_redmine(
                    redmine_user_id=redmine_user_id,
                    email=user["email"],
                    full_name=user["full_name"],
                    platform_role="project_manager",
                )

            has_password = bool((user.get("password_hash") or "").strip())
            if not has_password:
                generated_password = self._generate_password()
                self.users.update_password_hash(user["id"], hash_password(generated_password))

        if not user:
            raise ValueError("PM candidate not found in platform. Sync first.")

        self.entitlements.set_access(user["id"], enabled, admin_user_id)
        return {
            "user_id": user["id"],
            "redmine_user_id": user["redmine_user_id"],
            "email": user["email"],
            "enabled": enabled,
            "generated_password": generated_password,
        }

    @staticmethod
    def _generate_password(length: int = 14) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def list_pm_candidates(self) -> list[dict]:
        return self.users.list_project_managers_with_access()
    