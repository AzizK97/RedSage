import os
import requests
from langchain_core.tools import tool

# ── HTTP Helpers ───────────────────────────────────────────────────────────────

def _post(endpoint: str, payload: dict) -> dict:
    """Base authenticated POST request to Redmine."""
    redmine_url = os.getenv("REDMINE_URL", "http://localhost:3000")
    api_key     = os.getenv("REDMINE_API_KEY", "")

    response = requests.post(
        f"{redmine_url}{endpoint}",
        headers={
            "X-Redmine-API-Key": api_key,
            "Content-Type": "application/json"
        },
        json=payload
    )
    response.raise_for_status()
    # 201 Created returns a body, 200 may not
    try:
        return response.json()
    except Exception:
        return {"status": "success", "http_status": response.status_code}


def _put(endpoint: str, payload: dict) -> dict:
    """Base authenticated PUT request to Redmine."""
    redmine_url = os.getenv("REDMINE_URL", "http://localhost:3000")
    api_key     = os.getenv("REDMINE_API_KEY", "")

    response = requests.put(
        f"{redmine_url}{endpoint}",
        headers={
            "X-Redmine-API-Key": api_key,
            "Content-Type": "application/json"
        },
        json=payload
    )
    response.raise_for_status()
    try:
        return response.json()
    except Exception:
        return {"status": "success", "http_status": response.status_code}


# ── Issue Write Tools ──────────────────────────────────────────────────────────

@tool
def create_issue(
    project_id:     str,
    subject:        str,
    description:    str  = None,
    assigned_to_id: int  = None,
    priority_id:    int  = 4,
    status_id:      int  = 1,
    version_id:     int  = None,
    start_date:     str  = None,
    due_date:       str  = None,
) -> dict:
    """
    Create a new issue (ticket) in a Redmine project.
    Use when the user asks to create, add, or open a new task or ticket.

    Args:
        project_id:     Project identifier  e.g. 'ai-chatbot-platform'
        subject:        Title of the issue
        description:    Detailed description of the issue
        assigned_to_id: Numeric ID of the user to assign the issue to
        priority_id:    3=low  4=normal  5=high  6=urgent  (default: 4)
        status_id:      1=New  2=In Progress  3=Resolved  5=Closed  (default: 1)
        version_id:     Numeric sprint/version ID to assign the issue to
        start_date:     Start date in YYYY-MM-DD format
        due_date:       Due date in YYYY-MM-DD format
    """
    issue: dict = {
        "project_id": project_id,
        "subject":    subject,
        "priority_id": priority_id,
        "status_id":   status_id,
    }
    if description:    issue["description"]    = description
    if assigned_to_id: issue["assigned_to_id"] = assigned_to_id
    if version_id:     issue["fixed_version_id"] = version_id
    if start_date:     issue["start_date"]     = start_date
    if due_date:       issue["due_date"]        = due_date

    data = _post("/issues.json", {"issue": issue})
    created = data.get("issue", {})
    return {
        "status":  "created",
        "id":      created.get("id"),
        "subject": created.get("subject"),
        "url":     f"{os.getenv('REDMINE_URL')}/issues/{created.get('id')}"
    }


@tool
def update_issue_status(
    issue_id:  int,
    status_id: int,
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
        status_id: New status ID (see above)
        notes:     Optional comment to add when changing the status
    """
    payload: dict = {"issue": {"status_id": status_id}}
    if notes:
        payload["issue"]["notes"] = notes

    _put(f"/issues/{issue_id}.json", payload)
    status_names = {1: "New", 2: "In Progress", 3: "Resolved",
                    4: "Feedback", 5: "Closed", 6: "Rejected"}
    return {
        "status":    "updated",
        "issue_id":  issue_id,
        "new_status": status_names.get(status_id, str(status_id))
    }


@tool
def reassign_issue(
    issue_id:       int,
    assigned_to_id: int,
    notes:          str = None
) -> dict:
    """
    Reassign an existing Redmine issue to a different team member.
    Use when the user asks to assign, reassign, or transfer a task.

    Args:
        issue_id:       Numeric ID of the issue to reassign
        assigned_to_id: Numeric ID of the user to assign the issue to
        notes:          Optional comment to add when reassigning
    """
    payload: dict = {"issue": {"assigned_to_id": assigned_to_id}}
    if notes:
        payload["issue"]["notes"] = notes

    _put(f"/issues/{issue_id}.json", payload)
    return {
        "status":           "updated",
        "issue_id":         issue_id,
        "assigned_to_id":   assigned_to_id
    }


@tool
def add_comment_to_issue(
    issue_id: int,
    comment:  str
) -> dict:
    """
    Add a comment or note to an existing Redmine issue.
    Use when the user asks to comment on, annotate, or add a note to a task.

    Args:
        issue_id: Numeric ID of the issue
        comment:  The comment text to add
    """
    _put(f"/issues/{issue_id}.json", {"issue": {"notes": comment}})
    return {
        "status":   "comment_added",
        "issue_id": issue_id
    }


@tool
def update_issue_dates(
    issue_id:   int,
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

    _put(f"/issues/{issue_id}.json", {"issue": issue})
    return {
        "status":     "updated",
        "issue_id":   issue_id,
        "due_date":   due_date,
        "start_date": start_date
    }


# ── Time Entry Tools ───────────────────────────────────────────────────────────

@tool
def log_time(
    issue_id:    int,
    hours:       float,
    activity_id: int  = 9,
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
        "issue_id":    issue_id,
        "hours":       hours,
        "activity_id": activity_id
    }
    if comments: entry["comments"] = comments
    if spent_on: entry["spent_on"] = spent_on

    data = _post("/time_entries.json", {"time_entry": entry})
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
    project_id:  str,
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
    version: dict = {
        "name":   name,
        "status": status
    }
    if due_date:    version["due_date"]    = due_date
    if description: version["description"] = description

    data = _post(f"/projects/{project_id}/versions.json", {"version": version})
    created = data.get("version", {})
    return {
        "status":   "created",
        "id":       created.get("id"),
        "name":     created.get("name"),
        "due_date": created.get("due_date")
    }


@tool
def update_version_dates(
    version_id:  int,
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

    _put(f"/versions/{version_id}.json", {"version": version})
    return {
        "status":     "updated",
        "version_id": version_id,
        "changes":    version
    }