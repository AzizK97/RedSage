from dataclasses import dataclass
from fastapi import Depends, Header, HTTPException, status
from psycopg import Connection

from app.core.rbac import Permission, Role, has_permission
from app.core.security import decode_and_verify_jwt as decode
from app.dependencies.db import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.entitlement_repository import EntitlementRepository


@dataclass
class CurrentUser:
    id: str
    username: str
    full_name: str
    redmine_user_id: int
    role: Role
    enabled: bool

def get_current_user(
        authorization: str = Header(default=""),
        db: Connection = Depends(get_db),
) -> CurrentUser:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token"
        )
    
    token = authorization.replace("Bearer ", "", 1).strip()
    payload = decode(token)

    redmine_user_id = int(payload.get("redmine_user_id", 0))
    if redmine_user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    users= UserRepository(db)
    ents = EntitlementRepository(db)

    user = users.get_by_redmine_user_id(redmine_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not provisioned on platform"
        )
    
    enabled = ents.is_enabled(user["id"])
    email = str(user.get("email", "")).strip()
    username = email.split("@", 1)[0] if "@" in email else email or user["id"]

    return CurrentUser(
        id=user["id"],
        username=username,
        full_name=user.get("full_name", ""),
        redmine_user_id=user["redmine_user_id"],
        role=Role(user["platform_role"]),
        enabled=enabled
    )

def require_permission(permission: Permission):
    def _checker(current: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current.role != Role.ADMIN and not current.enabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access disabled by Admin"
            )
        if not has_permission(current.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden"
            )
        return current
    return _checker