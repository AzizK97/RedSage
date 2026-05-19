from psycopg import Connection
from app.integrations.redmine_client import redmine_client
from app.repositories.user_repository import UserRepository
from app.repositories.entitlement_repository import EntitlementRepository


class UserSyncService:
    def __init__(self, db: Connection) -> None:
        self.users = UserRepository(db)
        self.entitlements = EntitlementRepository(db)

    @staticmethod
    def _is_admin_candidate(user: dict) -> bool:
        return bool(user.get("admin"))

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

    def _role_for_user(self, user: dict) -> str:
        if self._is_admin_candidate(user):
            return "admin"
        
        # Check heuristic-based PM candidates (login/group name)
        if self._is_pm_candidate(user):
            return "project_manager"
        
        # Check if user has any managed projects via Redmine membership roles
        # This catches users classified as "Manager", "Lead", "Owner", etc. in project memberships
        # Use strict mode to avoid false positives from regular members
        try:
            managed_projects = redmine_client.list_managed_project_identifiers_for_user_strict(user["id"])
            if managed_projects:
                return "project_manager"
        except Exception:
            # If we can't check memberships, fall through to member
            pass
        
        return "member"

    def sync_all_active_users(self) -> int:
        """Mirror every active Redmine user into the platform DB.

        - Admins become `admin`
        - Manager-like users become `project_manager`
        - Everyone else becomes `member`
        - Missing entitlement rows are created as disabled, but existing access is preserved
        """
        synced = 0
        for user in redmine_client.list_users():
            role = self._role_for_user(user)
            saved = self.users.mirror_user_from_redmine(
                redmine_user_id=user["id"],
                email=user.get("mail", f"user{user['id']}@example.com"),
                full_name=f"{user.get('firstname','')} {user.get('lastname', '')}".strip() or user.get("login", ""),
                platform_role=role,
            )

            if not self.entitlements.has_access_record(saved["id"]):
                self.entitlements.set_access(saved["id"], False, admin_user_id="system")
            synced += 1

        return synced

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