from psycopg import Connection
from app.integrations.redmine_client import redmine_client
from app.repositories.user_repository import UserRepository
from app.repositories.entitlement_repository import EntitlementRepository


class UserSyncService:
    def __init__(self, db: Connection) -> None:
        self.users = UserRepository(db)
        self.entitlements = EntitlementRepository(db)

    @staticmethod
    def _is_pm_candidate(user: dict) -> bool:
        login = (user.get("login") or "").lower()
        if "manager" in login:
            return True
        
        for group in user.get("groups", []):
            name = (group.get("name") or "").lower()
            if "manager" in name:
                return True

        return False
    def sync_project_managers(self) -> int:

        synced = 0
        for user in redmine_client.list_users():
            is_pm = self._is_pm_candidate(user)
            if not is_pm:
                continue

            saved = self.users.mirror_user_from_redmine(
                redmine_user_id=user["id"],
                email=user.get("mail", f"user{user['id']}@example.com"),  # Fallback email if not provided
                full_name=f"{user.get('firstname','')} {user.get('lastname', '')}".strip() or user.get("login", ""),
                platform_role="project_manager",
            )

            if not self.entitlements.is_enabled(saved["id"]):
                self.entitlements.set_access(saved["id"], False, admin_user_id="system")
            synced += 1

        return synced