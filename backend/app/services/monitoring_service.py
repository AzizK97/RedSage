from __future__ import annotations

from typing import Any

import psycopg

from app.core.settings import settings
from app.monitoring.repository import MonitoringRepository
from app.monitoring.service import MonitoringService as MonitoringDataService

_SEVERITY_MAP: dict[str, str] = {
    "critical": "critical",
    "important": "warning",
    "info": "info",
}


class MonitoringService:
    """Facade over MonitoringDataService.

    All endpoints talk to this class.  Business logic (run, status, notifications,
    overview) is centralised here; low-level Redmine polling, event detection,
    Postgres persistence, and Slack dispatch are delegated to MonitoringDataService.
    """

    def __init__(self) -> None:
        self._data = MonitoringDataService()

    async def run_once(self) -> dict[str, Any]:
        return await self._data.run_once()

    async def get_overview(self) -> dict[str, Any]:
        return await self._data.get_overview()

    def last_result(self) -> dict[str, Any]:
        if not settings.PLATFORM_POSTGRES_URL:
            return {"status": "idle", "ran_at": None, "events_count": 0}

        with psycopg.connect(settings.PLATFORM_POSTGRES_URL) as db:
            repo = MonitoringRepository(db)
            repo.ensure_tables()
            overview = repo.get_overview()

        last_run = overview.get("last_run")
        if not last_run:
            return {"status": "idle", "ran_at": None, "events_count": 0}

        return {
            "status": "ok",
            "ran_at": last_run.get("started_at"),
            "projects_count": last_run.get("projects_count", 0),
            "issues_count": last_run.get("issues_count", 0),
            "events_count": last_run.get("events_count", 0),
        }

    def notifications(self) -> list[dict[str, Any]]:
        if not settings.PLATFORM_POSTGRES_URL:
            return []

        with psycopg.connect(settings.PLATFORM_POSTGRES_URL) as db:
            repo = MonitoringRepository(db)
            repo.ensure_tables()
            events = repo.get_recent_notifications()

        return [
            {
                "id": str(event["id"]),
                "title": event["title"],
                "subtitle": event["event_type"].replace("_", " ").title(),
                "message": event.get("details") or "",
                "severity": _SEVERITY_MAP.get(event["severity"], "info"),
                # Milliseconds since epoch, matching the rest of the app's
                # timestamps (the frontend's timeAgo expects ms). Returning
                # seconds here made every item read as ~20k days ago.
                "created_at": (
                    int(event["occurred_at"].timestamp() * 1000)
                    if event.get("occurred_at")
                    else None
                ),
            }
            for event in events
        ]
