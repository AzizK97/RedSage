from psycopg import Connection
from app.repositories.user_repository import UserRepository
from app.repositories.entitlement_repository import EntitlementRepository


class AdminService:
    def __init__(self, db: Connection) -> None:
        self.users = UserRepository(db)
        self.entitlements = EntitlementRepository(db)

    def set_pm_access(self, admin_user_id: str, redmine_user_id: int, enabled: bool) -> dict:

        user = self.users.get_by_redmine_user_id(redmine_user_id)
        if not user:
            raise ValueError("PM candidate not found in platform. Sync first.")

        self.entitlements.set_access(user["id"], enabled, admin_user_id)
        return {
            "user_id": user["id"],
            "redmine_user_id": user["redmine_user_id"],
            "enabled": enabled,
        }
    