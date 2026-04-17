from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection

from app.core.rbac import Permission
from app.dependencies.auth import CurrentUser, require_permission
from app.dependencies.db import get_db
from app.schemas.admin import SetPmAccessRequest
from app.services.admin_service import AdminService
from app.services.user_sync_service import UserSyncService

router = APIRouter(prefix="/api/admin/users", tags=["admin_users"])


@router.post("/sync-pm")
def sync_pm_candidates(
    _: CurrentUser = Depends(require_permission(Permission.PM_ACCESS_MANAGE)),
    db: Connection = Depends(get_db),
):
    synced = UserSyncService(db).sync_project_managers()
    return {"synced_count": synced}

@router.post("/pm-access")
def set_pm_access(
    payload: SetPmAccessRequest,
    current: CurrentUser = Depends(require_permission(Permission.PM_ACCESS_MANAGE)),
    db: Connection = Depends(get_db),
):
    try:
        result = AdminService(db).set_pm_access(
            admin_user_id=current.id,
            redmine_user_id=payload.redmine_user_id,
            enabled=payload.enabled,
        )
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc