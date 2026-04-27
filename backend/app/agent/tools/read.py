import os
import requests
from datetime import date
from langchain_core.tools import tool

from app.agent.cache import get_cached, set_cached

# ── HTTP Helper ────────────────────────────────────────────────────────────────

def _get(endpoint: str, params: dict | None = None) -> dict:
    """Base authenticated GET request to Redmine."""
    redmine_url = os.getenv("REDMINE_URL", "http://localhost:3000").rstrip("/")
    api_key     = os.getenv("REDMINE_API_KEY", "")
    timeout_seconds = float(os.getenv("REDMINE_TIMEOUT_SECONDS", "10"))

    try:
        response = requests.get(
            f"{redmine_url}{endpoint}",
            headers={
                "X-Redmine-API-Key": api_key,
                "Content-Type": "application/json"
            },
            params=params or {},
            timeout=timeout_seconds,
        )
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"REDMINE_UNAVAILABLE: Unable to reach Redmine at '{redmine_url}'. "
            "Make sure Redmine is running and REDMINE_URL is correct."
        ) from exc

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        response_body = (response.text or "").strip()
        raise RuntimeError(
            f"REDMINE_API_ERROR: GET {endpoint} failed with HTTP {response.status_code}. "
            f"Response: {response_body or 'empty response'}"
        ) from exc

    return response.json()


def _as_str_id(value):
    if value is None:
        return None
    return str(value)


def _resolve_fixed_version_id(project_id: str, version_id: str | int | None) -> str | None:
    """Resolve a sprint/version reference to a Redmine fixed_version_id.

    Redmine's issues endpoint expects the version identifier, while the agent may
    pass a human-readable sprint label like "Sprint 3". If the value already
    looks numeric, keep it. Otherwise, look up the project's versions and match
    by id or name.
    """
    if version_id is None:
        return None

    version_text = str(version_id).strip()
    if not version_text:
        return None

    if version_text.isdigit():
        return version_text

    versions_payload = _get(f"/projects/{project_id}/versions.json")
    for version in versions_payload.get("versions", []):
        version_name = str(version.get("name", "")).strip()
        version_identifier = str(version.get("identifier", "")).strip()
        if version_text == version_name or version_text == version_identifier:
            version_id_value = version.get("id")
            if version_id_value is not None:
                return str(version_id_value)

    return version_text


# ── Read Tools ─────────────────────────────────────────────────────────────────

@tool
def get_projects() -> dict:
    """
    Retrieve all available Redmine projects.
    Use this tool when the user asks about available projects,
    or when you need to resolve a project name to its identifier.
    """

    # cache_key = "redmine:projects"
    # cached = await get_cached(cache_key)

    # if cached:
    #     return cached

    data = _get("/projects.json", {"limit": 100})
    result = {
        "total_count": data.get("total_count", 0),
        "projects": [
            {
                "id":          p["id"],
                "name":        p["name"],
                "identifier":  p["identifier"],
                "description": p.get("description", "")
            }
            for p in data.get("projects", [])
        ]
    }

    # await set_cached(cache_key, result, ttl_seconds=3600)  # Cache for 1 hour
    return result


@tool
def get_issues(
    project_id:     str,
    status_id:      str | int = "open",
    priority_id:    str | int | None = None,
    assigned_to_id: str | int | None = None,
    due_before:     str | None = None,
    version_id:     str | int | None = None,
    limit:          int = 50
) -> dict:
    """
    Retrieve Redmine issues with dynamic filters.
    Use for any question about tasks — status, priority, assignee, deadlines.

    Args:
        project_id:     Project identifier  e.g. 'ai-chatbot-platform'
        status_id:      'open', 'closed', or '*' for all
        priority_id:    '1'=low  '2'=normal  '3'=high  '4'=urgent '5'=immediate
        assigned_to_id: User/assignee ID (string or integer)
        due_before:     YYYY-MM-DD — returns tasks whose due date <= this date
        version_id:     Sprint/version ID (string or integer)
        limit:          Max results to return (default 50)
    """

    params: dict = {
        "project_id": project_id,
        "status_id":  _as_str_id(status_id),
        "limit":      limit
    }
    if priority_id:
        params["priority_id"] = _as_str_id(priority_id)
    if assigned_to_id:
        params["assigned_to_id"] = _as_str_id(assigned_to_id)
    if due_before:
        params["due_date"] = f"<={due_before}"
    if version_id:
        params["fixed_version_id"] = _resolve_fixed_version_id(project_id, version_id)

    data = _get("/issues.json", params)
    result =  {
        "total_count": data.get("total_count", 0),
        "issues": [
            {
                "id":          i["id"],
                "subject":     i["subject"],
                "status":      i["status"]["name"],
                "priority":    i["priority"]["name"],
                "assigned_to": i.get("assigned_to", {}).get("name", "Unassigned"),
                "due_date":    i.get("due_date", "Not set"),
                "project":     i["project"]["name"],
                "version":     i.get("fixed_version", {}).get("name", "No sprint")
            }
            for i in data.get("issues", [])
        ]
    }

    return result



@tool
def get_members(project_id: str) -> dict:
    """
    Retrieve all members of a Redmine project with their roles.
    Use when the user asks about the team, members, or roles.

    Args:
        project_id: Project identifier  e.g. 'ai-chatbot-platform'
    """

    data = _get(f"/projects/{project_id}/memberships.json")
    result = {
        "total_count": len(data.get("memberships", [])),
        "members": [
            {
                "id":    m["user"]["id"],
                "name":  m["user"]["name"],
                "roles": [r["name"] for r in m.get("roles", [])]
            }
            for m in data.get("memberships", [])
            if "user" in m
        ]
    }
    return result

@tool
def get_versions(project_id: str) -> dict:
    """
    Retrieve all versions (sprints/milestones) of a Redmine project.
    Use when the user asks about sprints, milestones, planning, or deadlines.

    Args:
        project_id: Project identifier  e.g. 'ai-chatbot-platform'
    """

    data  = _get(f"/projects/{project_id}/versions.json")
    today = date.today().isoformat()

    def normalize_due_date(value):
        if isinstance(value, str) and value.strip():
            return value
        return None

    result = {
        "total_count": len(data.get("versions", [])),
        "versions": [
            {
                "id":         v["id"],
                "name":       v["name"],
                "status":     v["status"],
                "due_date":   normalize_due_date(v.get("due_date")) or "Not set",
                "is_overdue": (
                    bool(normalize_due_date(v.get("due_date")))
                    and normalize_due_date(v.get("due_date")) < today
                    and v.get("status") != "closed"
                )
            }
            for v in data.get("versions", [])
        ]
    }

    return result


@tool
def get_issue_detail(issue_id: int | str) -> dict:
    """
    Retrieve the full details of a specific Redmine issue by its ID.
    Use when the user asks about a specific ticket or task by number.

    Args:
        issue_id: Numeric ID of the issue  e.g. 42
    """
    data  = _get(f"/issues/{_as_str_id(issue_id)}.json")
    issue = data.get("issue", {})
    return {
        "id":          issue.get("id"),
        "subject":     issue.get("subject"),
        "description": issue.get("description", "No description"),
        "status":      issue.get("status", {}).get("name"),
        "priority":    issue.get("priority", {}).get("name"),
        "assigned_to": issue.get("assigned_to", {}).get("name", "Unassigned"),
        "author":      issue.get("author", {}).get("name"),
        "project":     issue.get("project", {}).get("name"),
        "version":     issue.get("fixed_version", {}).get("name", "No sprint"),
        "start_date":  issue.get("start_date", "Not set"),
        "due_date":    issue.get("due_date", "Not set"),
        "done_ratio":  issue.get("done_ratio", 0),
        "created_on":  issue.get("created_on"),
        "updated_on":  issue.get("updated_on")
    }