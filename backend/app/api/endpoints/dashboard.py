from fastapi import APIRouter, Depends
from datetime import datetime, timezone
import requests

from app.core.rbac import Permission, Role
from app.dependencies.auth import CurrentUser, require_permission
from app.integrations.redmine_client import redmine_client

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/projects")
def list_dashboard_projects(
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
):
    projects = redmine_client.list_projects()
    if current.role == Role.ADMIN:
        return {"items": projects}

    managed_project_identifiers = set(
        redmine_client.list_managed_project_identifiers_for_user(current.redmine_user_id)
    )
    scoped_projects = [
        project
        for project in projects
        if (project.get("identifier") or "") in managed_project_identifiers
    ]
    return {"items": scoped_projects}


@router.get("/insights")
def list_dashboard_insights(
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
):
    projects = redmine_client.list_projects()
    if current.role != Role.ADMIN:
        allowed_identifiers = set(
            redmine_client.list_managed_project_identifiers_for_user(current.redmine_user_id)
        )
        projects = [
            project for project in projects if (project.get("identifier") or "") in allowed_identifiers
        ]

    overdue_items: list[dict] = []
    at_risk_projects: list[dict] = []
    today_iso = datetime.now(timezone.utc).date().isoformat()

    for project in projects:
        identifier = (project.get("identifier") or "").strip()
        if not identifier:
            continue

        resp = requests.get(
            f"{redmine_client.base_url}/issues.json",
            headers=redmine_client.headers,
            params={
                "project_id": identifier,
                "status_id": "*",
                "limit": 100,
                "offset": 0,
            },
            timeout=20,
        )
        if resp.status_code >= 400:
            continue
        issues = resp.json().get("issues", [])
        if not issues:
            continue

        project_overdue = 0
        project_high_priority = 0
        for issue in issues:
            status_name = str((issue.get("status") or {}).get("name", "")).lower()
            if "closed" in status_name:
                continue
            due_date = issue.get("due_date")
            priority_name = str((issue.get("priority") or {}).get("name", "")).lower()
            is_high_priority = any(
                tag in priority_name for tag in ("high", "urgent", "immediate", "critical")
            )
            if is_high_priority:
                project_high_priority += 1
            if due_date and due_date < today_iso:
                project_overdue += 1
                overdue_items.append(
                    {
                        "issue_id": issue.get("id"),
                        "subject": issue.get("subject"),
                        "project_name": project.get("name"),
                        "project_identifier": identifier,
                        "due_date": due_date,
                        "priority": (issue.get("priority") or {}).get("name", ""),
                        "status": (issue.get("status") or {}).get("name", ""),
                        "url": f"{redmine_client.base_url}/issues/{issue.get('id')}",
                    }
                )

        if project_overdue > 0 or project_high_priority >= 3:
            reason = (
                f"{project_overdue} overdue issue(s)"
                if project_overdue > 0
                else f"{project_high_priority} high-priority open issue(s)"
            )
            at_risk_projects.append(
                {
                    "project_id": project.get("id"),
                    "project_name": project.get("name"),
                    "project_identifier": identifier,
                    "overdue_count": project_overdue,
                    "high_priority_open_count": project_high_priority,
                    "reason": reason,
                    "recommended_action": (
                        "Review overdue backlog and re-plan sprint scope"
                        if project_overdue > 0
                        else "Triage high-priority queue and assign owners"
                    ),
                    "url": f"{redmine_client.base_url}/projects/{identifier}",
                }
            )

    overdue_items.sort(key=lambda item: (item.get("due_date") or "9999-12-31",))
    at_risk_projects.sort(
        key=lambda item: (-(item.get("overdue_count") or 0), -(item.get("high_priority_open_count") or 0))
    )
    return {
        "top_overdue_tickets": overdue_items[:8],
        "at_risk_projects": at_risk_projects[:6],
    }
