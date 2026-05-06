from fastapi import APIRouter, Depends
from datetime import datetime, timezone
import requests

from app.core.rbac import Permission, Role
from app.dependencies.auth import CurrentUser, require_permission
from app.integrations.redmine_client import redmine_client

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _fetch_project_versions(project_identifier: str) -> list[dict]:
    """Fetch project versions (sprints / milestones)."""

    resp = requests.get(
        f"{redmine_client.base_url}/projects/{project_identifier}/versions.json",
        headers=redmine_client.headers,
        timeout=20,
    )
    if resp.status_code >= 400:
        return []

    return resp.json().get("versions", [])


def _fetch_project_issues(project_id: str | int, fixed_version_id: str | int | None = None) -> list[dict]:
    """Fetch all issues for a single Redmine project, optionally filtered by version."""

    issues: list[dict] = []
    offset = 0
    limit = 100
    params: dict[str, object] = {
        "project_id": project_id,
        "status_id": "*",
        "limit": limit,
        "offset": offset,
    }
    if fixed_version_id is not None:
        params["fixed_version_id"] = fixed_version_id

    while True:
        params["offset"] = offset
        resp = requests.get(
            f"{redmine_client.base_url}/issues.json",
            headers=redmine_client.headers,
            params=params,
            timeout=20,
        )
        if resp.status_code >= 400:
            return []

        payload = resp.json()
        chunk = payload.get("issues", [])
        issues.extend(chunk)

        total_count = int(payload.get("total_count", len(issues)))
        if len(chunk) < limit or len(issues) >= total_count:
            break
        offset += limit

    return issues


def _issue_weight(issue: dict) -> float:
    estimated_hours = issue.get("estimated_hours")
    try:
        weight = float(estimated_hours)
        return weight if weight > 0 else 1.0
    except (TypeError, ValueError):
        return 1.0


def _issue_completion(issue: dict) -> int:
    status_name = str((issue.get("status") or {}).get("name", "")).lower()
    if any(keyword in status_name for keyword in ("closed", "resolved", "rejected", "done", "verified", "fixed")):
        return 100

    raw_done_ratio = issue.get("done_ratio", 0) or 0
    try:
        return max(0, min(100, int(raw_done_ratio)))
    except (TypeError, ValueError):
        return 0


def _build_project_status(project: dict, today_iso: str) -> dict:
    project_id = project.get("id") or project.get("identifier") or ""
    project_identifier = (project.get("identifier") or "").strip()
    versions = _fetch_project_versions(project_identifier) if project_identifier else []
    active_versions = [
        version
        for version in versions
        if str(version.get("status", "")).lower() in {"open", "locked"}
    ]

    issues: list[dict] = []
    if active_versions:
        for version in active_versions:
            version_id = version.get("id")
            if version_id is None:
                continue
            issues.extend(_fetch_project_issues(project_id, fixed_version_id=version_id))

    if not issues:
        issues = _fetch_project_issues(project_id)

    total_issues = len(issues)
    if total_issues == 0:
        return {
            "progress": 0,
            "health": "At risk",
            "completion_eta": "No issues yet",
            "open_issues": 0,
            "closed_issues": 0,
            "overdue_issues": 0,
            "total_issues": 0,
        }

    progress_sum = 0.0
    total_weight = 0.0
    open_issues = 0
    closed_issues = 0
    overdue_issues = 0
    due_dates: list[str] = []

    for issue in issues:
        completion = _issue_completion(issue)
        weight = _issue_weight(issue)
        total_weight += weight
        progress_sum += completion * weight

        status_name = str((issue.get("status") or {}).get("name", "")).lower()
        is_closed = completion == 100 or any(
            keyword in status_name
            for keyword in ("closed", "resolved", "rejected", "done", "verified", "fixed")
        )

        if is_closed:
            closed_issues += 1
        else:
            open_issues += 1
            due_date = issue.get("due_date")
            if due_date:
                due_dates.append(due_date)
                if due_date < today_iso:
                    overdue_issues += 1

    progress = round(progress_sum / total_weight) if total_weight > 0 else 0
    if overdue_issues > 0:
        health: str = "Delayed"
    elif total_issues == 0:
        health = "At risk"
    elif progress < 60:
        health = "At risk"
    else:
        health = "On track"

    if active_versions:
        version_due_dates = [str(v.get("due_date") or "") for v in active_versions if v.get("due_date")]
        completion_eta = min(version_due_dates) if version_due_dates else ("No due dates" if open_issues > 0 else "No open issues")
    else:
        completion_eta = min(due_dates) if due_dates else ("No open issues" if open_issues == 0 else "No due dates")

    return {
        "progress": progress,
        "health": health,
        "completion_eta": completion_eta,
        "open_issues": open_issues,
        "closed_issues": closed_issues,
        "overdue_issues": overdue_issues,
        "total_issues": total_issues,
    }


@router.get("/projects")
def list_dashboard_projects(
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
):
    projects = redmine_client.list_projects()
    if current.role == Role.ADMIN:
        scoped_projects = projects
    else:
        managed_project_identifiers = set(
            redmine_client.list_managed_project_identifiers_for_user(current.redmine_user_id)
        )
        scoped_projects = [
            project
            for project in projects
            if (project.get("identifier") or "") in managed_project_identifiers
        ]

    today_iso = datetime.now(timezone.utc).date().isoformat()
    items: list[dict] = []
    for project in scoped_projects:
        items.append({
            **project,
            **_build_project_status(project, today_iso),
        })

    return {"items": items}


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

        issues = _fetch_project_issues(project.get("id") or identifier)
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
