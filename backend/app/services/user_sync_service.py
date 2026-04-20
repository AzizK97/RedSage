from psycopg import Connection
from app.integrations.redmine_client import redmine_client
from app.repositories.user_repository import UserRepository
from app.repositories.entitlement_repository import EntitlementRepository


class UserSyncService:
    def __init__(self, db: Connection) -> None:
        self.users = UserRepository(db)
        self.entitlements = EntitlementRepository(db)

    @staticmethod
    def _has_manager_role(membership: dict) -> bool:
        for role in membership.get("roles", []):
            role_name = str(role.get("name", "")).strip().lower()
            if role_name == "manager":
                return True
        return False

    def sync_project_managers(self) -> int:

        users = redmine_client.list_users()
        user_by_id = {int(user["id"]): user for user in users if "id" in user}

        manager_user_ids: set[int] = set()
        for project in redmine_client.list_projects():
            project_key = project.get("identifier") or project.get("id")
            if not project_key:
                continue

            memberships = redmine_client.list_project_memberships(project_key)
            for membership in memberships:
                membership_user = membership.get("user")
                if not membership_user:
                    continue

                if self._has_manager_role(membership):
                    manager_user_ids.add(int(membership_user["id"]))

        synced = 0
        for manager_user_id in sorted(manager_user_ids):
            user = user_by_id.get(manager_user_id)
            if not user:
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

        existing_pm_rows = self.users.list_project_managers_with_access()
        for pm in existing_pm_rows:
            if int(pm["redmine_user_id"]) in manager_user_ids:
                continue

            self.users.mirror_user_from_redmine(
                redmine_user_id=int(pm["redmine_user_id"]),
                email=pm["email"],
                full_name=pm["full_name"],
                platform_role="member",
            )

        return synced