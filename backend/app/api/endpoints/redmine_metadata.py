"""Expose Redmine metadata needed by the approval dialogs."""

from fastapi import APIRouter, Depends

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


@router.get("/redmine-metadata", include_in_schema=False)
def redmine_metadata(_current: CurrentUser = Depends(require_permission(Permission.CHAT_USE))) -> dict:
    return {
        "base_url": redmine_client.base_url,
        "trackers": _normalize_options(redmine_client.list_trackers()),
        "issue_statuses": _normalize_options(redmine_client.list_issue_statuses()),
        "issue_priorities": _normalize_options(redmine_client.list_issue_priorities()),
    }
