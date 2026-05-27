from fastapi import APIRouter, Depends

from app.core.rbac import Permission
from app.dependencies.auth import CurrentUser, require_permission
from app.monitoring.service import MonitoringService as MonitoringDataService
from app.services.monitoring_service import MonitoringService as MonitoringStatusService

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])
monitoring_status_service = MonitoringStatusService()
monitoring_data_service = MonitoringDataService()


@router.post("/run-now")
async def run_monitoring_now(
    _: CurrentUser = Depends(require_permission(Permission.PM_ACCESS_MANAGE)),
):
    return await monitoring_data_service.run_once()


@router.get("/status")
def monitoring_status(
    _: CurrentUser = Depends(require_permission(Permission.PM_ACCESS_MANAGE)),
):
    return monitoring_status_service.last_result()


@router.get("/overview")
async def monitoring_overview(
    _: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
):
    return await monitoring_data_service.get_overview()


@router.get("/notifications")
def monitoring_notifications(
    _: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
):
    return {"items": monitoring_status_service.notifications()}
