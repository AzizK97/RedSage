from datetime import datetime, timezone, timedelta

from .analyzer import analyze_issues
from .config import settings
from .fetcher import RedmineFetcher
from .notifier import notify_slack
from .storage import MonitoringStorage


class MonitoringService:
    def __init__(self):
        self.storage = MonitoringStorage(settings.SQLITE_PATH)
        self.fetcher = RedmineFetcher()

    async def run_once(self) -> dict:
        endpoint = self.fetcher.ENDPOINT
        now = datetime.now(timezone.utc)

        last_sync = self.storage.get_last_sync(endpoint)
        if last_sync is None:
            last_sync = now - timedelta(days=2)

        issues = await self.fetcher.fetch_changed_issues(last_sync)
        alerts = analyze_issues(issues)

        notified = 0
        for alert in alerts:
            should_notify = self.storage.upsert_alert(alert, settings.MONITORING_ALERT_COOLDOWN_SECONDS)
            if should_notify:
                await notify_slack(alert)
                notified += 1

        # coarse metrics snapshot from fetched set (MVP)
        open_count = len(issues)
        overdue_count = sum(1 for a in alerts if a["type"] == "overdue")
        due_soon_count = sum(1 for a in alerts if a["type"] == "due_soon")
        self.storage.insert_metrics(now, open_count, overdue_count, due_soon_count)

        self.storage.set_last_sync(endpoint, now)

        return {
            "fetched_issues": len(issues),
            "alerts_detected": len(alerts),
            "alerts_notified": notified,
            "last_sync": now.isoformat(),
        }

    def list_alerts(self, limit: int = 200) -> list[dict]:
        return self.storage.list_alerts(limit)

    def get_stats(self, limit: int = 200) -> list[dict]:
        return self.storage.get_metrics(limit)