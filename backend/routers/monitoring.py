from fastapi import APIRouter, Query

from monitoring.service import MonitoringService

router = APIRouter(prefix="/monitoring", tags=["monitoring"])
svc = MonitoringService()


@router.get("/health")
async def health():
    return {"ok": True}


@router.post("/run-once")
async def run_once():
    return await svc.run_once()


@router.get("/alerts")
async def alerts(limit: int = Query(default=200, ge=1, le=1000)):
    return {"items": svc.list_alerts(limit)}


@router.get("/stats")
async def stats(limit: int = Query(default=200, ge=1, le=1000)):
    return {"items": svc.get_stats(limit)}