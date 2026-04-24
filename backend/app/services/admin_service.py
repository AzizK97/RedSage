from psycopg import Connection
from app.integrations.redmine_client import redmine_client
from app.repositories.user_repository import UserRepository
from app.repositories.entitlement_repository import EntitlementRepository


class AdminService:
    def __init__(self, db: Connection) -> None:
        self.users = UserRepository(db)
        self.entitlements = EntitlementRepository(db)

    def set_pm_access(self, admin_user_id: str, redmine_user_id: int, enabled: bool) -> dict:
        user = self.users.get_by_redmine_user_id(redmine_user_id)
        generated_account = False
        if not user and enabled:
            redmine_user = redmine_client.get_user(redmine_user_id)
            if not redmine_user:
                raise ValueError("Redmine user was not found.")

            full_name = (
                f"{redmine_user.get('firstname', '')} {redmine_user.get('lastname', '')}".strip()
                or redmine_user.get("login", "")
            )
            email = redmine_user.get("mail", f"user{redmine_user_id}@example.com")
            user = self.users.mirror_user_from_redmine(
                redmine_user_id=redmine_user_id,
                email=email,
                full_name=full_name,
                platform_role="project_manager",
            )
            generated_account = True

        if not user:
            raise ValueError("PM candidate not found in platform. Sync first or enable access to auto-provision.")

        self.entitlements.set_access(user["id"], enabled, admin_user_id)
        access_state = self.entitlements.get_access_state(user["id"])
        return {
            "user_id": user["id"],
            "redmine_user_id": user["redmine_user_id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "enabled": enabled,
            "generated_account": generated_account,
            "enabled_by_admin_id": access_state["enabled_by_admin_id"],
        }

    def list_pm_candidates(self) -> dict:
        users = self.users.list_by_role("project_manager")
        items = []
        for user in users:
            access_state = self.entitlements.get_access_state(user["id"])
            items.append(
                {
                    "redmine_user_id": user["redmine_user_id"],
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "in_platform": True,
                    "enabled": access_state["enabled"],
                    "credentials_ready": True,
                }
            )

        return {"items": items}
    