from datetime import datetime, timedelta, timezone

from .config import settings
from .schemas import MonitoringIssue


CLOSED_STATUS_IDS = {5}  
HIGH_PRIORITY_IDS = {3, 4, 5}  


def analyze_issues(issues: list[MonitoringIssue]) -> list[dict]:
    now = datetime.now(timezone.utc)
    out: list[dict] = []

    for issue in issues:
        is_closed = issue.status_id in CLOSED_STATUS_IDS

        if issue.due_date and not is_closed:
            due_dt = datetime.combine(issue.due_date, datetime.min.time(), tzinfo=timezone.utc)
            if due_dt < now:
                out.append({
                    "key": f"overdue:issue:{issue.id}",
                    "type": "overdue",
                    "severity": "high",
                    "issue_id": issue.id,
                    "project_id": issue.project_id,
                    "message": f"Issue #{issue.id} is overdue.",
                    "detected_at": now.isoformat(),
                })
            elif due_dt <= now + timedelta(hours=settings.MONITORING_DUE_SOON_HOURS):
                out.append({
                    "key": f"due_soon:issue:{issue.id}:{issue.due_date}",
                    "type": "due_soon",
                    "severity": "medium",
                    "issue_id": issue.id,
                    "project_id": issue.project_id,
                    "message": f"Issue #{issue.id} is due soon ({issue.due_date}).",
                    "detected_at": now.isoformat(),
                })

        if not is_closed and issue.updated_on < (now - timedelta(days=settings.MONITORING_STALE_DAYS)):
            out.append({
                "key": f"stale:issue:{issue.id}",
                "type": "stale",
                "severity": "medium",
                "issue_id": issue.id,
                "project_id": issue.project_id,
                "message": f"Issue #{issue.id} is stale (no updates).",
                "detected_at": now.isoformat(),
            })

        if (issue.priority_id in HIGH_PRIORITY_IDS) and (issue.assigned_to_id is None) and not is_closed:
            out.append({
                "key": f"unassigned_high_priority:issue:{issue.id}",
                "type": "unassigned_high_priority",
                "severity": "high",
                "issue_id": issue.id,
                "project_id": issue.project_id,
                "message": f"High-priority issue #{issue.id} is unassigned.",
                "detected_at": now.isoformat(),
            })

    return out