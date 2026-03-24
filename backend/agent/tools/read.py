import os
import requests
from datetime import date
from langchain_core.tools import tool

# ── HTTP Helper ────────────────────────────────────────────────────────────────

def _get(endpoint: str, params: dict = {}) -> dict:
    """Base authenticated GET request to Redmine."""
    redmine_url = os.getenv("REDMINE_URL", "http://localhost:3000")
    api_key     = os.getenv("REDMINE_API_KEY", "")

    response = requests.get(
        f"{redmine_url}{endpoint}",
        headers={
            "X-Redmine-API-Key": api_key,
            "Content-Type": "application/json"
        },
        params=params
    )
    response.raise_for_status()
    return response.json()


# ── Read Tools ─────────────────────────────────────────────────────────────────

@tool
def get_projects() -> dict:
    """
    Retrieve all available Redmine projects.
    Use this tool when the user asks about available projects,
    or when you need to resolve a project name to its identifier.
    """
    data = _get("/projects.json", {"limit": 100})
    return {
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


@tool
def get_issues(
    project_id:     str,
    status_id:      str = "open",
    priority_id:    str = None,
    assigned_to_id: str = None,
    due_before:     str = None,
    version_id:     str = None,
    limit:          int = 50
) -> dict:
    """
    Retrieve Redmine issues with dynamic filters.
    Use for any question about tasks — status, priority, assignee, deadlines.

    Args:
        project_id:     Project identifier  e.g. 'ai-chatbot-platform'
        status_id:      'open', 'closed', or '*' for all
        priority_id:    '1'=low  '2'=normal  '3'=high  '4'=urgent '5'=immediate
        assigned_to_id: Numeric user ID of the assignee
        due_before:     YYYY-MM-DD — returns tasks whose due date <= this date
        version_id:     Numeric sprint/version ID
        limit:          Max results to return (default 50)
    """
    params: dict = {
        "project_id": project_id,
        "status_id":  status_id,
        "limit":      limit
    }
    if priority_id:
        params["priority_id"] = priority_id
    if assigned_to_id:
        params["assigned_to_id"] = assigned_to_id
    if due_before:
        params["due_date"] = f"<={due_before}"
    if version_id:
        params["fixed_version_id"] = version_id

    data = _get("/issues.json", params)
    return {
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


@tool
def get_members(project_id: str) -> dict:
    """
    Retrieve all members of a Redmine project with their roles.
    Use when the user asks about the team, members, or roles.

    Args:
        project_id: Project identifier  e.g. 'ai-chatbot-platform'
    """
    data = _get(f"/projects/{project_id}/memberships.json")
    return {
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
    return {
        "total_count": len(data.get("versions", [])),
        "versions": [
            {
                "id":         v["id"],
                "name":       v["name"],
                "status":     v["status"],
                "due_date":   v.get("due_date", "Not set"),
                "is_overdue": (
                    v.get("due_date", "9999") < today
                    and v["status"] != "closed"
                )
            }
            for v in data.get("versions", [])
        ]
    }


@tool
def get_issue_detail(issue_id: int) -> dict:
    """
    Retrieve the full details of a specific Redmine issue by its ID.
    Use when the user asks about a specific ticket or task by number.

    Args:
        issue_id: Numeric ID of the issue  e.g. 42
    """
    data  = _get(f"/issues/{issue_id}.json")
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