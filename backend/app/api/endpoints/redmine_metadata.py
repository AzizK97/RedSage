"""Expose Redmine metadata needed by the approval dialogs."""

from fastapi import APIRouter, Depends, Query

from app.core.rbac import Permission
from app.dependencies.auth import CurrentUser, require_permission
from app.integrations.redmine_client import redmine_client

router = APIRouter(prefix="/api/internal", tags=["internal"])


def _normalize_options(items: list[dict], label_keys: tuple[str, ...] = ("name", "label", "title")) -> list[dict]:
    options: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id")
        label = ""
        for key in label_keys:
            value = item.get(key)
            if value:
                label = str(value).strip()
                break
        if item_id is None or not label:
            continue
        options.append({"id": str(item_id), "name": label})
    return options


def _normalize_version_statuses() -> list[dict]:
    return [
        {"id": "open", "name": "Open"},
        {"id": "locked", "name": "Locked"},
        {"id": "closed", "name": "Closed"},
    ]


def _build_issue_summary(issue: dict | None) -> dict | None:
    if not issue:
        return None

    assignee = issue.get("assigned_to") or {}
    project = issue.get("project") or {}

    return {
        "id": str(issue.get("id") or ""),
        "subject": str(issue.get("subject") or "").strip(),
        "assigned_to_name": str(assignee.get("name") or "Unassigned").strip() or "Unassigned",
        "assigned_to_id": assignee.get("id"),
        "project_name": str(project.get("name") or "").strip(),
        "project_identifier": str(project.get("identifier") or "").strip(),
    }


@router.get("/redmine-metadata", include_in_schema=False)
def redmine_metadata(
    _current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    project_identifier: str | None = Query(default=None),
    issue_id: str | None = Query(default=None),
) -> dict:
    payload = {
        "base_url": redmine_client.base_url,
        "trackers": _normalize_options(redmine_client.list_trackers()),
        "issue_statuses": _normalize_options(redmine_client.list_issue_statuses()),
        "issue_priorities": _normalize_options(redmine_client.list_issue_priorities()),
        "version_statuses": _normalize_version_statuses(),
    }

    if project_identifier:
        payload["project_versions"] = _normalize_options(redmine_client.list_project_versions(project_identifier))
        payload["project_members"] = _normalize_options(redmine_client.list_project_members(project_identifier))

    if issue_id:
        issue = redmine_client.get_issue(issue_id)
        payload["issue_summary"] = _build_issue_summary(issue)

        if not project_identifier and issue:
            project = issue.get("project") or {}
            project_id = project.get("id")
            if project_id is not None:
                project_detail = redmine_client.get_project(project_id)
                project_identifier = (project_detail or {}).get("identifier") or project_identifier

            if project_identifier:
                payload["project_versions"] = _normalize_options(redmine_client.list_project_versions(project_identifier))
                payload["project_members"] = _normalize_options(redmine_client.list_project_members(project_identifier))

    return payload
