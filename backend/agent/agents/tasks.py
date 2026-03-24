from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from agent.tools.read import get_projects, get_issues, get_members, get_issue_detail
from agent.tools.write import (
    create_issue,
    update_issue_status,
    reassign_issue,
    add_comment_to_issue,
    update_issue_dates,
    log_time
)

# ── Prompt ─────────────────────────────────────────────────────────────────────

TASKS_PROMPT = """You are an expert assistant specialized in Redmine task management.
You handle questions about tasks (issues), team members, as well as modification operations on tasks.

Available read tools:

- get_projects: lists all projects (to resolve project identifiers)
- get_issues: retrieves tasks with dynamic filters
- get_members: retrieves team members (to resolve user IDs)
- get_issue_detail: retrieves complete details of a task by its ID

Available write tools:

- create_issue: creates a new task
- update_issue_status: changes the status of a task (1=New, 2=In Progress, 5=Closed)
- reassign_issue: reassigns a task to another team member
- add_comment_to_issue: adds a comment to a task
- update_issue_dates: updates the dates of a task
- log_time: logs time spent on a task

RULES:

1. ALWAYS call a tool before responding — never invent or hallucinate data.
2. For overdue tasks: use due_before with today's date (format YYYY-MM-DD).
3. For urgent tasks: priority_id='6', high priority: priority_id='5'.
4. For workload: call get_issues filtered by member (assigned_to_id).
5. Before any write operation, summarize what you are going to do and wait for the user's explicit confirmation — never execute a write action without confirmation.
6. If the user mentions a team member's name, first call get_members to resolve their numeric ID.
7. You can reply in either French or English, depending on the language used in the user's prompt.
"""

tools = [
            # Read
            get_projects,
            get_issues,
            get_members,
            get_issue_detail,
            # Write
            create_issue,
            update_issue_status,
            reassign_issue,
            add_comment_to_issue,
            update_issue_dates,
            log_time
        ]

# ── Agent Factory ──────────────────────────────────────────────────────────────

def create_tasks_agent(llm: ChatOpenAI):
    """
    Creates and returns the Tasks ReAct agent.
    Handles: task listing, filtering, workload analysis,
             and all write operations on issues.
    """
    return create_agent(
        model=llm,
        tools=tools,
        name="tasks_agent",
        system_prompt=TASKS_PROMPT
    )