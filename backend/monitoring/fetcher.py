from datetime import datetime, timedelta, timezone
import httpx

from .config import settings
from .schemas import MonitoringIssue


def _to_dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


class RedmineFetcher:
    ENDPOINT = "issues"

    async def fetch_changed_issues(self, since: datetime) -> list[MonitoringIssue]:
        overlap_since = since - timedelta(seconds=settings.MONITORING_OVERLAP_SECONDS)
        updated_filter = f">={overlap_since.strftime('%Y-%m-%dT%H:%M:%SZ')}"

        headers = {"X-Redmine-API-Key": settings.REDMINE_API_KEY}
        issues: list[MonitoringIssue] = []
        offset = 0
        limit = settings.REDMINE_PAGE_SIZE

        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                params = {
                    "status_id": "*",
                    "updated_on": updated_filter,
                    "limit": limit,
                    "offset": offset,
                }
                r = await client.get(f"{settings.REDMINE_BASE_URL}/issues.json", headers=headers, params=params)
                r.raise_for_status()
                payload = r.json()
                batch = payload.get("issues", [])

                if not batch:
                    break

                for i in batch:
                    issues.append(MonitoringIssue(
                        id=i["id"],
                        project_id=i["project"]["id"],
                        subject=i.get("subject", ""),
                        status_id=i["status"]["id"],
                        priority_id=i["priority"]["id"],
                        assigned_to_id=(i.get("assigned_to") or {}).get("id"),
                        due_date=i.get("due_date"),
                        updated_on=_to_dt(i["updated_on"]),
                    ))

                offset += limit

        return issues