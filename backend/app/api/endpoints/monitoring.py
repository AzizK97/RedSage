from fastapi import APIRouter, Depends

from app.core.rbac import Permission
from app.dependencies.auth import CurrentUser, require_permission
from app.monitoring.service import MonitoringService

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])
service = MonitoringService()


@router.get("/overview")
async def get_overview(
    _: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
):
    return await service.get_overview()


@router.post("/run")
async def run_monitoring_once(
    _: CurrentUser = Depends(require_permission(Permission.PM_ACCESS_MANAGE)),
):
    return await service.run_once()
