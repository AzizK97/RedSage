from fastapi import APIRouter, Depends

from app.core.rbac import Permission
from app.dependencies.auth import CurrentUser, require_permission
from app.services.monitoring_service import MonitoringService

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])
monitoring_service = MonitoringService()


@router.post("/run-now")
def run_monitoring_now(
    _: CurrentUser = Depends(require_permission(Permission.PM_ACCESS_MANAGE)),
):
    return monitoring_service.run_once()


@router.get("/status")
def monitoring_status(
    _: CurrentUser = Depends(require_permission(Permission.PM_ACCESS_MANAGE)),
):
    return monitoring_service.last_result()


@router.get("/overview")
def monitoring_overview(
    _: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
):
    return monitoring_service.get_overview()


@router.get("/notifications")
def monitoring_notifications(
    _: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
):
    return {"items": monitoring_service.notifications()}
