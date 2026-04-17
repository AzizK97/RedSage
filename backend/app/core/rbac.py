from enum import Enum
from typing import Set

class Role(str, Enum):
    ADMIN = "admin"
    PROJECT_MANAGER = "project_manager"

class Permission(str, Enum):
    CHAT_USE = "chat:use"
    SESSION_READ_OWN = "session:read:own"
    SESSION_READ_ALL = "session:read:all"
    PM_ACCESS_MANAGE = "pm_access:manage"

ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.PROJECT_MANAGER: {
        Permission.CHAT_USE,
        Permission.SESSION_READ_OWN,
    },
    Role.ADMIN: {
        Permission.CHAT_USE,
        Permission.SESSION_READ_OWN,
        Permission.SESSION_READ_ALL,
        Permission.PM_ACCESS_MANAGE
    }
}

def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())