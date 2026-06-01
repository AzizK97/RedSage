from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from app.agent.tools.read import (
    get_today,
    get_projects,
    get_issues,
    get_all_issues,
    get_project_metrics,
    get_all_projects_metrics,
    get_members,
    get_issue_detail,
)
from app.agent.tools.write import (
    create_issue,
    update_issue_status,
    reassign_issue,
    add_comment_to_issue,
    update_issue_dates,
    log_time
)
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langfuse import Langfuse

tools = [
    get_today,
    get_projects,
    get_issues,
    get_all_issues,
    get_project_metrics,
    get_all_projects_metrics,
    get_members,
    get_issue_detail,

    create_issue,
    update_issue_status,
    reassign_issue,
    add_comment_to_issue,
    update_issue_dates,
    log_time,
]

CREATE_ISSUE_SCHEMA = {
    "type": "object",
    "properties": {
        "project_id": {"type": "string", "title": "Project"},
        "tracker_id": {"type": "string", "title": "Tracker"},
        "subject": {"type": "string", "title": "Subject"},
        "description": {"type": "string", "title": "Notes / Description"},
        "status_id": {"type": "string", "title": "Status"},
        "priority_id": {"type": "string", "title": "Priority"},
        "assigned_to_id": {"type": "string", "title": "Assignee"},
        "version_id": {"type": "string", "title": "Target version"},
        "start_date": {"type": "string", "title": "Start date"},
        "due_date": {"type": "string", "title": "Due date"},
    },
    "required": ["project_id", "subject"],
}

UPDATE_ISSUE_STATUS_SCHEMA = {
    "type": "object",
    "properties": {
        "issue_id": {"type": "string", "title": "Issue"},
        "status_id": {"type": "string", "title": "Status"},
        "notes": {"type": "string", "title": "Notes"},
    },
    "required": ["issue_id", "status_id"],
}

REASSIGN_ISSUE_SCHEMA = {
    "type": "object",
    "properties": {
        "issue_id": {"type": "string", "title": "Issue"},
        "assigned_to_id": {"type": "string", "title": "Assignee"},
        "notes": {"type": "string", "title": "Notes"},
    },
    "required": ["issue_id", "assigned_to_id"],
}

ADD_COMMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "issue_id": {"type": "string", "title": "Issue"},
        "comment": {"type": "string", "title": "Comment"},
    },
    "required": ["issue_id", "comment"],
}

UPDATE_ISSUE_DATES_SCHEMA = {
    "type": "object",
    "properties": {
        "issue_id": {"type": "string", "title": "Issue"},
        "due_date": {"type": "string", "title": "Due date"},
        "start_date": {"type": "string", "title": "Start date"},
    },
    "required": ["issue_id"],
}

LOG_TIME_SCHEMA = {
    "type": "object",
    "properties": {
        "issue_id": {"type": "string", "title": "Issue"},
        "hours": {"type": "number", "title": "Hours"},
        "activity_id": {"type": "string", "title": "Activity"},
        "comments": {"type": "string", "title": "Comments"},
        "spent_on": {"type": "string", "title": "Spent on"},
    },
    "required": ["issue_id", "hours"],
}

interrupt_on = {
    "create_issue":
        {"allowed_decisions": ["approve", "reject", "edit"], "description": "Review the new issue details before creating it.", "args_schema": CREATE_ISSUE_SCHEMA
        },
    
    "update_issue_status":
        {"allowed_decisions": ["approve", "reject", "edit"], "description": "Review the issue status change before applying it.", "args_schema": UPDATE_ISSUE_STATUS_SCHEMA
        },
    
    "reassign_issue":
        {"allowed_decisions": ["approve", "reject", "edit"], "description": "Review the assignee change before applying it.", "args_schema": REASSIGN_ISSUE_SCHEMA
        },
    
    "add_comment_to_issue":
        {"allowed_decisions": ["approve", "reject", "edit"], "description": "Review the comment that will be added to the issue.", "args_schema": ADD_COMMENT_SCHEMA
        },
    
    "update_issue_dates":
        {"allowed_decisions": ["approve", "reject", "edit"], "description": "Review the date change before updating the issue.", "args_schema": UPDATE_ISSUE_DATES_SCHEMA
        },
    
    "log_time":
        {"allowed_decisions": ["approve", "reject", "edit"], "description": "Review the time entry before logging it.", "args_schema": LOG_TIME_SCHEMA
        }
    }

def create_tasks_agent(llm: ChatOpenAI):
    """
    Creates and returns the Tasks ReAct agent.
    Handles: task listing, filtering, workload analysis,
             and all write operations on issues.
    """
    TASKS_LOCAL_RULES = """
Task handling rules:
- Treat task, issue, ticket, and bug as the same work item class.
- If the user says "this week", use get_today and apply an exact date range for the current week when possible.
- Prefer precise filters over speculative follow-up searches.
- If a search returns no results, say so plainly and stop; do not invent another time bucket like next week or overdue unless the user explicitly asks.
- When the user has not specified a project, assume all projects and use get_all_issues.
- Never fabricate task rows, dates, assignees, or priorities.
""".strip()

    TASKS_PROMPT = TASKS_LOCAL_RULES
    try:
        compiled_prompt = Langfuse().get_prompt("tasks_agent", label="latest").compile()
        TASKS_PROMPT = "\n".join(
            m["content"] for m in compiled_prompt if m.get("role") == "system"
        )
        TASKS_PROMPT = f"{TASKS_PROMPT}\n\n{TASKS_LOCAL_RULES}"
    except Exception as e:
        print("Error loading prompt from Langfuse:", e)
        # Fall back to the local rules only if Langfuse prompt loading fails.

    return create_agent(
        model=llm,
        tools=tools,
        name="tasks_agent",
        system_prompt=TASKS_PROMPT,
        middleware=[
            HumanInTheLoopMiddleware(interrupt_on=interrupt_on)
            ]
    )