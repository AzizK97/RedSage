from langchain_core.tools import tool

from app.integrations.redmine_client import redmine_client


def _as_str_id(value):
    if value is None:
        return None
    return str(value)


def _resolve_version_id(project_id, version_id) -> str | None:
    """Resolve a version reference to a real Redmine version id.

    The model often passes a sprint *name* or number (e.g. "0" for "sprint 0")
    as the version_id. Sending that straight to Redmine yields HTTP 422
    ("Target version is not included in the list"). We look the value up among
    the project's versions, matching by id first then by name, and omit it
    (return None) when it cannot be resolved rather than send an invalid value.
    """
    if version_id is None:
        return None
    raw = str(version_id).strip()
    if not raw:
        return None

    try:
        versions = redmine_client.list_project_versions(project_id) if project_id else []
    except Exception:
        versions = []

    if not versions:
        # Could not list versions; only trust a plausible real id (positive int).
        return raw if raw.isdigit() and int(raw) > 0 else None

    by_id = {str(v.get("id")) for v in versions if v.get("id") is not None}
    if raw in by_id:
        return raw

    target = raw.lower()
    target_compact = target.replace("sprint", "").strip()
    for v in versions:
        name = str(v.get("name", "")).strip().lower()
        if not name:
            continue
        name_compact = name.replace("sprint", "").strip()
        if target in (name, name_compact) or target_compact in (name, name_compact):
            return str(v.get("id"))

    # Unresolvable reference -> omit rather than send an invalid version.
    return None


# ── Issue Write Tools ──────────────────────────────────────────────────────────

@tool
def create_issue(
    project_id:     str | None,
    subject:        str,
    tracker_id:     int | str | None = None,
    description:    str  = None,
    assigned_to_id: int | str | None  = None,
    priority_id:    int | str  = 4,
    status_id:      int | str  = 1,
    version_id:     int | str | None  = None,
    start_date:     str  = None,
    due_date:       str  = None,
) -> dict:
    """
    Create a new issue (ticket) in a Redmine project.
    Use when the user asks to create, add, or open a new task or ticket.

    Args:
        project_id:     Project identifier  e.g. 'ai-chatbot-platform'
        tracker_id:     Tracker ID to use for the issue (string or integer)
        subject:        Title of the issue
        description:    Detailed description of the issue
        assigned_to_id: User ID to assign the issue to (string or integer)
        priority_id:    1=low  2=normal  3=high  4=urgent 5=immediate  (default: 2)
        status_id:      1=New  2=In Progress  3=Resolved  5=Closed  (default: 1)
        version_id:     Sprint/version ID to assign the issue to (string or integer)
        start_date:     Start date in YYYY-MM-DD format
        due_date:       Due date in YYYY-MM-DD format
    """
    # Allow callers to omit project_id; fall back to session default.
    from app.agent.tools.read import get_session_project

    if project_id is None:
        project_id = get_session_project()

    if not project_id:
        raise RuntimeError("MISSING_PROJECT_ID: project_id is required and no session default is set.")

    issue: dict = {
        "project_id": project_id,
        "tracker_id": _as_str_id(tracker_id) if tracker_id is not None else None,
        "subject":    subject,
        "priority_id": _as_str_id(priority_id),
        "status_id":   _as_str_id(status_id),
    }
    if issue["tracker_id"] is None:
        issue.pop("tracker_id")
    if description:    issue["description"]    = description
    if assigned_to_id is not None: issue["assigned_to_id"] = _as_str_id(assigned_to_id)
    if version_id is not None:
        resolved_version = _resolve_version_id(project_id, version_id)
        if resolved_version is not None:
            issue["fixed_version_id"] = resolved_version
    if start_date:     issue["start_date"]     = start_date
    if due_date:       issue["due_date"]        = due_date

    data = redmine_client.post("/issues.json", {"issue": issue})
    created = data.get("issue", {})
    return {
        "status":  "created",
        "id":      created.get("id"),
        "subject": created.get("subject"),
        "url":     f"{redmine_client.base_url}/issues/{created.get('id')}"
    }


@tool
def update_issue_status(
    issue_id:  int | str,
    status_id: int | str,
    notes:     str = None
) -> dict:
    """
    Update the status of an existing Redmine issue.
    Use when the user asks to open, start, resolve, or close a task.

    Status IDs:
        1 = New
        2 = In Progress
        3 = Resolved
        4 = Feedback
        5 = Closed
        6 = Rejected

    Args:
        issue_id:  Numeric ID of the issue to update
        status_id: New status ID (see above; string or integer)
        notes:     Optional comment to add when changing the status
    """
    payload: dict = {"issue": {"status_id": _as_str_id(status_id)}}
    if notes:
        payload["issue"]["notes"] = notes

    redmine_client.put(f"/issues/{_as_str_id(issue_id)}.json", payload)
    status_names = {"1": "New", "2": "In Progress", "3": "Resolved",
                    "4": "Feedback", "5": "Closed", "6": "Rejected"}
    return {
        "status":    "updated",
        "issue_id":  issue_id,
        "new_status": status_names.get(str(status_id), str(status_id))
    }


@tool
def reassign_issue(
    issue_id:       int | str,
    assigned_to_id: int | str,
    notes:          str = None
) -> dict:
    """
    Reassign an existing Redmine issue to a different team member.
    Use when the user asks to assign, reassign, or transfer a task.

    Args:
        issue_id:       Numeric ID of the issue to reassign
        assigned_to_id: User ID to assign the issue to (string or integer)
        notes:          Optional comment to add when reassigning
    """
    payload: dict = {"issue": {"assigned_to_id": _as_str_id(assigned_to_id)}}
    if notes:
        payload["issue"]["notes"] = notes

    redmine_client.put(f"/issues/{_as_str_id(issue_id)}.json", payload)
    return {
        "status":           "updated",
        "issue_id":         issue_id,
        "assigned_to_id":   assigned_to_id
    }


@tool
def add_comment_to_issue(
    issue_id: int | str,
    comment:  str
) -> dict:
    """
    Add a comment or note to an existing Redmine issue.
    Use when the user asks to comment on, annotate, or add a note to a task.

    Args:
        issue_id: Numeric ID of the issue
        comment:  The comment text to add
    """
    redmine_client.put(f"/issues/{_as_str_id(issue_id)}.json", {"issue": {"notes": comment}})
    return {
        "status":   "comment_added",
        "issue_id": issue_id
    }


@tool
def update_issue_dates(
    issue_id:   int | str,
    due_date:   str = None,
    start_date: str = None
) -> dict:
    """
    Update the start date or due date of an existing Redmine issue.
    Use when the user asks to extend, postpone, or update a task deadline.

    Args:
        issue_id:   Numeric ID of the issue
        due_date:   New due date in YYYY-MM-DD format
        start_date: New start date in YYYY-MM-DD format
    """
    issue: dict = {}
    if due_date:   issue["due_date"]   = due_date
    if start_date: issue["start_date"] = start_date

    if not issue:
        return {"status": "error", "message": "No dates provided."}

    redmine_client.put(f"/issues/{_as_str_id(issue_id)}.json", {"issue": issue})
    return {
        "status":     "updated",
        "issue_id":   issue_id,
        "due_date":   due_date,
        "start_date": start_date
    }


# ── Time Entry Tools ───────────────────────────────────────────────────────────

@tool
def log_time(
    issue_id:    int | str,
    hours:       float,
    activity_id: int | str  = 9,
    comments:    str  = None,
    spent_on:    str  = None
) -> dict:
    """
    Log time spent on a Redmine issue.
    Use when the user asks to log, record, or track time on a task.

    Common activity IDs:
        9  = Design
        10 = Development (default)
        11 = Testing
        12 = Documentation

    Args:
        issue_id:    Numeric ID of the issue
        hours:       Number of hours to log  e.g. 2.5
        activity_id: Activity type ID (default: 10 = Development)
        comments:    Optional description of work done
        spent_on:    Date in YYYY-MM-DD format (defaults to today)
    """
    entry: dict = {
        "issue_id":    _as_str_id(issue_id),
        "hours":       hours,
        "activity_id": _as_str_id(activity_id)
    }
    if comments: entry["comments"] = comments
    if spent_on: entry["spent_on"] = spent_on

    data = redmine_client.post("/time_entries.json", {"time_entry": entry})
    created = data.get("time_entry", {})
    return {
        "status":      "logged",
        "time_entry_id": created.get("id"),
        "issue_id":    issue_id,
        "hours":       hours
    }


# ── Version (Sprint) Write Tools ───────────────────────────────────────────────

@tool
def create_version(
    project_id:  str | None,
    name:        str,
    due_date:    str  = None,
    description: str  = None,
    status:      str  = "open"
) -> dict:
    """
    Create a new version (sprint or milestone) in a Redmine project.
    Use when the user asks to create a new sprint, milestone, or version.

    Args:
        project_id:  Project identifier  e.g. 'ai-chatbot-platform'
        name:        Name of the sprint  e.g. 'Sprint 4 - Testing'
        due_date:    Due date in YYYY-MM-DD format
        description: Optional description of the sprint
        status:      'open' or 'locked' or 'closed'  (default: 'open')
    """
    # Allow callers to omit project_id; fall back to session default.
    from app.agent.tools.read import get_session_project

    if project_id is None:
        project_id = get_session_project()

    if not project_id:
        raise RuntimeError("MISSING_PROJECT_ID: project_id is required and no session default is set.")

    version: dict = {
        "name":   name,
        "status": status
    }
    if due_date:    version["due_date"]    = due_date
    if description: version["description"] = description

    data = redmine_client.post(f"/projects/{project_id}/versions.json", {"version": version})
    created = data.get("version", {})
    return {
        "status":   "created",
        "id":       created.get("id"),
        "name":     created.get("name"),
        "due_date": created.get("due_date")
    }


@tool
def update_version_dates(
    version_id:  int | str,
    due_date:    str  = None,
    name:        str  = None,
    status:      str  = None,
    description: str  = None
) -> dict:
    """
    Update a Redmine version (sprint) — its name, due date, or status.
    Use when the user asks to rename, reschedule, or close a sprint.

    Args:
        version_id:  Numeric ID of the version/sprint
        due_date:    New due date in YYYY-MM-DD format
        name:        New name for the sprint
        status:      'open', 'locked', or 'closed'
        description: New description
    """
    version: dict = {}
    if due_date:    version["due_date"]    = due_date
    if name:        version["name"]        = name
    if status:      version["status"]      = status
    if description: version["description"] = description

    if not version:
        return {"status": "error", "message": "No fields provided to update."}

    redmine_client.put(f"/versions/{_as_str_id(version_id)}.json", {"version": version})
    return {
        "status":     "updated",
        "version_id": version_id,
        "changes":    version
    }