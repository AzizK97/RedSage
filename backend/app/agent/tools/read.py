import os
import requests
from datetime import date
from langchain_core.tools import tool

from app.agent.cache import get_cached, set_cached, get_cached_sync, set_cached_sync

# Session-level state set by supervisor before invoking the agent.
_SESSION_REDMINE_USER_ID: int | None = None
_SESSION_IS_ADMIN: bool = False
_ALLOWED_PROJECT_IDENTIFIERS: set[str] | None = None


def set_session_user(redmine_user_id: int | None, is_admin: bool = False):
    """Configure the current session's Redmine user and compute allowed projects.

    If `is_admin` is True, no project filtering is applied (access to all projects).
    Otherwise, this will query Redmine to find projects where the Redmine user
    holds a managerial role and restrict tools to those projects.
    """
    global _SESSION_REDMINE_USER_ID, _SESSION_IS_ADMIN, _ALLOWED_PROJECT_IDENTIFIERS
    _SESSION_REDMINE_USER_ID = redmine_user_id
    _SESSION_IS_ADMIN = bool(is_admin)
    _ALLOWED_PROJECT_IDENTIFIERS = None

    if redmine_user_id is None or _SESSION_IS_ADMIN:
        return

    try:
        # Try cache first
        cache_key = f"allowed_projects:{redmine_user_id}"
        cached = get_cached_sync(cache_key)
        if cached is not None:
            _ALLOWED_PROJECT_IDENTIFIERS = set(cached)
            return

        # Build a set of project identifiers that this user manages.
        projects = _get("/projects.json", {"limit": 100}).get("projects", [])
        allowed: set[str] = set()

        for p in projects:
            identifier = p.get("identifier")
            if not identifier:
                continue
            try:
                members = _get(f"/projects/{identifier}/memberships.json").get("memberships", [])
            except Exception:
                continue

            for m in members:
                user = m.get("user") or {}
                if user.get("id") == redmine_user_id:
                    # If any role name contains 'manager', consider it managerial.
                    for r in m.get("roles", []):
                        if "manager" in (r.get("name") or "").lower():
                            allowed.add(identifier)
                            break
                    else:
                        # continue outer loop
                        continue
                    break

        _ALLOWED_PROJECT_IDENTIFIERS = allowed
        # Store into cache for subsequent calls
        try:
            set_cached_sync(cache_key, list(allowed), ttl_seconds=3600)
        except Exception:
            pass
    except Exception:
        # Fail closed: if we cannot determine allowed projects, disallow access.
        _ALLOWED_PROJECT_IDENTIFIERS = set()


def clear_session_user():
    global _SESSION_REDMINE_USER_ID, _SESSION_IS_ADMIN, _ALLOWED_PROJECT_IDENTIFIERS
    _SESSION_REDMINE_USER_ID = None
    _SESSION_IS_ADMIN = False
    _ALLOWED_PROJECT_IDENTIFIERS = None

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
    projects = [
        {
            "id":          p["id"],
            "name":        p["name"],
            "identifier":  p["identifier"],
            "description": p.get("description", "")
        }
        for p in data.get("projects", [])
    ]

    # If session filtering is active, filter projects to allowed identifiers.
    if _ALLOWED_PROJECT_IDENTIFIERS is not None:
        projects = [p for p in projects if p.get("identifier") in _ALLOWED_PROJECT_IDENTIFIERS]

    result = {
        "total_count": len(projects),
        "projects": projects
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
        params["fixed_version_id"] = _as_str_id(version_id)

    # Enforce session-level project restrictions when present.
    if _ALLOWED_PROJECT_IDENTIFIERS is not None:
        # If there are no allowed projects, return empty result.
        if not _ALLOWED_PROJECT_IDENTIFIERS:
            return {"total_count": 0, "issues": []}
        # If the requested project is not allowed, return empty result.
        if str(project_id) not in _ALLOWED_PROJECT_IDENTIFIERS:
            return {"total_count": 0, "issues": []}

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

    if _ALLOWED_PROJECT_IDENTIFIERS is not None:
        if not _ALLOWED_PROJECT_IDENTIFIERS or project_id not in _ALLOWED_PROJECT_IDENTIFIERS:
            return {"total_count": 0, "members": []}

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

    if _ALLOWED_PROJECT_IDENTIFIERS is not None:
        if not _ALLOWED_PROJECT_IDENTIFIERS or project_id not in _ALLOWED_PROJECT_IDENTIFIERS:
            return {"total_count": 0, "versions": []}

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

    # If session filtering is active, ensure the issue's project is allowed.
    if _ALLOWED_PROJECT_IDENTIFIERS is not None:
        if not _ALLOWED_PROJECT_IDENTIFIERS:
            raise RuntimeError("UNAUTHORIZED: no accessible projects for this session")

        proj = issue.get("project", {})
        proj_id = proj.get("id")
        proj_identifier = None
        if proj_id is not None:
            try:
                proj_data = _get(f"/projects/{proj_id}.json")
                proj_identifier = proj_data.get("project", {}).get("identifier")
            except Exception:
                proj_identifier = None

        if proj_identifier is None or proj_identifier not in _ALLOWED_PROJECT_IDENTIFIERS:
            raise RuntimeError("UNAUTHORIZED: project not accessible in this session")
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