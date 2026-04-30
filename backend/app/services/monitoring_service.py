from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Any

from app.monitoring.workflow import run_monitoring_workflow


class MonitoringService:
    def __init__(self) -> None:
        self._lock = Lock()
        self._notification_feed: list[dict[str, Any]] = []
        self._last_result: dict[str, Any] = {
            "status": "idle",
            "ran_at": None,
            "summary": "",
            "notification": {},
            "slack_sent": False,
            "error": "",
            "events": [],
        }

    def run_once(self) -> dict[str, Any]:
        with self._lock:
            result = run_monitoring_workflow()
            ran_at = datetime.now(timezone.utc).isoformat()
            self._last_result = {
                "status": "ok" if not result.get("error") else "error",
                "ran_at": ran_at,
                "summary": result.get("summary", ""),
                "notification": result.get("notification", {}),
                "slack_sent": bool(result.get("slack_sent")),
                "error": result.get("error", ""),
                "events": result.get("events", []),
            }
            notification = self._last_result["notification"] or {}
            self._notification_feed.insert(
                0,
                {
                    "id": f"monitoring-{ran_at}",
                    "created_at": ran_at,
                    "title": notification.get("title", "Monitoring update"),
                    "subtitle": notification.get("subtitle", ""),
                    "message": notification.get("message", self._last_result["summary"]),
                    "severity": notification.get("severity", "info"),
                    "action_text": notification.get("action_text", ""),
                    "action_url": notification.get("action_url", "/"),
                    "slack_sent": self._last_result["slack_sent"],
                    "status": self._last_result["status"],
                },
            )
            self._notification_feed = self._notification_feed[:50]
            return self._last_result

    def last_result(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._last_result)

    def notifications(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._notification_feed)
