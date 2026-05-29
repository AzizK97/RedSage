import os
import requests
from datetime import date, timedelta
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
def get_today() -> dict:
    """
    Returns today's date and useful derived date strings.
    ALWAYS call this first when the user's question involves any time-relative
    concept: 'today', 'this week', 'overdue', 'due soon', 'this sprint',
    'urgent now', 'tomorrow', 'next week', or any date range.
    Never ask the user for the current date.
    """
    today = date.today()
    week_end = today + timedelta(days=(6 - today.weekday()))
    tomorrow = today + timedelta(days=1)
    next_week_end = week_end + timedelta(days=7)
    return {
        "today": today.isoformat(),
        "tomorrow": tomorrow.isoformat(),
        "week_end": week_end.isoformat(),       # end of current ISO week (Sunday)
        "next_week_end": next_week_end.isoformat(),
        "day_of_week": today.strftime("%A"),
    }

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
def get_all_issues(
    status_id: str = "open",
    priority_id: str | None = None,
    due_before: str | None = None,
    due_after: str | None = None,
) -> dict:
    """
    Retrieve issues across ALL accessible projects in one call.
    Use when the user asks about issues without specifying a project,
    or says 'all projects', 'everything', 'across all projects',
    'what needs attention', 'what is critical today', etc.
    Respects RBAC: project managers only see their allowed projects.

    Args:
        status_id:   'open', 'closed', or '*' for all (default 'open')
        priority_id: '1'=low '2'=normal '3'=high '4'=urgent '5'=immediate
        due_before:  YYYY-MM-DD — upper bound on due date
        due_after:   YYYY-MM-DD — lower bound on due date
                     Set both to the same value for exact date match.
    """
    data = _get("/projects.json", {"limit": 100})
    projects = data.get("projects", [])

    if _ALLOWED_PROJECT_IDENTIFIERS is not None:
        projects = [
            p for p in projects
            if p.get("identifier") in _ALLOWED_PROJECT_IDENTIFIERS
        ]

    all_issues = []

    for p in projects:
        identifier = p.get("identifier")
        if not identifier:
            continue

        params: dict = {
            "project_id": identifier,
            "status_id": str(status_id),
            "limit": 100,
        }
        if priority_id:
            params["priority_id"] = str(priority_id)

        # Apply date filter — use >= when we have due_after, else <=
        if due_after:
            params["due_date"] = f">={due_after}"
        try:
            result = _get("/issues.json", params)
            issues = result.get("issues", [])

            # Post-filter upper bound for range queries
            if due_before and due_after:
                issues = [
                    i for i in issues
                    if i.get("due_date") and i["due_date"] <= due_before
                ]

            all_issues.extend(issues)
        except Exception:
            continue

    return {
        "total_count": len(all_issues),
        "issues": [
            {
                "id": i["id"],
                "subject": i["subject"],
                "status": i["status"]["name"],
                "priority": i["priority"]["name"],
                "assigned_to": i.get("assigned_to", {}).get("name", "Unassigned"),
                "due_date": i.get("due_date", "Not set"),
                "project": i["project"]["name"],
                "version": i.get("fixed_version", {}).get("name", "No sprint"),
            }
            for i in all_issues
        ],
    }

@tool
def get_issues(
    project_id:     str,
    status_id:      str | int = "open",
    priority_id:    str | int | None = None,
    assigned_to_id: str | int | None = None,
    due_before:     str | None = None,
    due_after:      str | None = None,
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
        due_before:     YYYY-MM-DD — returns issues whose due date <= this date
        due_after:      YYYY-MM-DD — returns issues whose due date >= this date
                        For exact date: set both due_before=X and due_after=X
                        For a range: set due_after=start and due_before=end
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
    if due_before and due_after:
        # Range query: use Redmine's >= filter via API, then post-filter in Python
        # Redmine only supports one due_date operator at a time
        params["due_date"] = f">={due_after}"
    elif due_before:
        params["due_date"] = f"<={due_before}"
    elif due_after:
        params["due_date"] = f">={due_after}"
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
    raw_issues = data.get("issues", [])

    # Post-filter for range queries: Redmine only supports one due_date
    # operator per request, so we apply the upper bound in Python.
    if due_before and due_after:
        raw_issues = [
            i for i in raw_issues
            if i.get("due_date") and i["due_date"] <= due_before
        ]

    result = {
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
            for i in raw_issues
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


@tool
def get_project_metrics(project_id: str) -> dict:
    """
    Calculate completion and other quick metrics for a single project.

    Returns:
        total_issues, open, closed, completion_pct, overdue_open, urgent_open,
        and a short list of top open issues (by priority & due date).
    """
    if _ALLOWED_PROJECT_IDENTIFIERS is not None:
        if not _ALLOWED_PROJECT_IDENTIFIERS or project_id not in _ALLOWED_PROJECT_IDENTIFIERS:
            return {"project": project_id, "total_issues": 0, "open": 0, "closed": 0, "completion_pct": None, "overdue_open": 0, "urgent_open": 0, "top_open": []}

    today = date.today().isoformat()

    open_count = _get("/issues.json", {"project_id": project_id, "status_id": "open", "limit": 1}).get("total_count", 0)
    closed_count = _get("/issues.json", {"project_id": project_id, "status_id": "closed", "limit": 1}).get("total_count", 0)
    total = open_count + closed_count
    completion_pct = None
    if total > 0:
        completion_pct = round((closed_count / total) * 100, 1)

    # Overdue open issues (due <= today and still open)
    overdue_open = _get("/issues.json", {"project_id": project_id, "status_id": "open", "due_date": f"<={today}", "limit": 1}).get("total_count", 0)

    # Urgent open issues: aggregate priority 4 and 5 (urgent / immediate)
    urgent_open = 0
    try:
        urgent_open += _get("/issues.json", {"project_id": project_id, "status_id": "open", "priority_id": "4", "limit": 1}).get("total_count", 0)
        urgent_open += _get("/issues.json", {"project_id": project_id, "status_id": "open", "priority_id": "5", "limit": 1}).get("total_count", 0)
    except Exception:
        urgent_open = 0

    # Fetch a sample of open issues to surface top items
    sample = []
    try:
        data = _get("/issues.json", {"project_id": project_id, "status_id": "open", "limit": 100})
        issues = data.get("issues", [])
        # Sort by priority id desc (if present) then due_date asc
        def sort_key(i):
            pri = (i.get("priority") or {}).get("id") or 0
            due = i.get("due_date") or "9999-99-99"
            return (-int(pri), due)

        issues_sorted = sorted(issues, key=sort_key)
        for i in issues_sorted[:5]:
            sample.append({
                "id": i.get("id"),
                "subject": i.get("subject"),
                "priority": i.get("priority", {}).get("name"),
                "assigned_to": i.get("assigned_to", {}).get("name", "Unassigned"),
                "due_date": i.get("due_date", "Not set"),
                "status": i.get("status", {}).get("name"),
            })
    except Exception:
        sample = []

    return {
        "project": project_id,
        "total_issues": total,
        "open": open_count,
        "closed": closed_count,
        "completion_pct": completion_pct,
        "overdue_open": overdue_open,
        "urgent_open": urgent_open,
        "top_open": sample,
    }


@tool
def get_all_projects_metrics() -> dict:
    """
    Compute basic metrics for all accessible projects and return a summary.

    Returns per-project metrics (as in `get_project_metrics`) and aggregate totals.
    """
    data = _get("/projects.json", {"limit": 100})
    projects = data.get("projects", [])

    if _ALLOWED_PROJECT_IDENTIFIERS is not None:
        projects = [p for p in projects if p.get("identifier") in _ALLOWED_PROJECT_IDENTIFIERS]

    metrics = []
    agg = {"total_projects": 0, "total_issues": 0, "open": 0, "closed": 0, "overdue_open": 0, "urgent_open": 0}

    for p in projects:
        identifier = p.get("identifier")
        if not identifier:
            continue
        m = get_project_metrics(identifier)
        metrics.append({"project_name": p.get("name"), "identifier": identifier, **m})
        agg["total_projects"] += 1
        agg["total_issues"] += m.get("total_issues", 0) or 0
        agg["open"] += m.get("open", 0) or 0
        agg["closed"] += m.get("closed", 0) or 0
        agg["overdue_open"] += m.get("overdue_open", 0) or 0
        agg["urgent_open"] += m.get("urgent_open", 0) or 0

    # Compute overall completion
    agg_completion = None
    if agg["total_issues"] > 0:
        agg_completion = round((agg["closed"] / agg["total_issues"]) * 100, 1)

    return {"summary": {**agg, "completion_pct": agg_completion}, "projects": metrics}