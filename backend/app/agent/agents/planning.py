from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from app.agent.tools.read import get_today, get_projects, get_versions, get_issues, get_project_metrics
from app.agent.tools.write import create_version, update_version_dates
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langfuse import  Langfuse

tools = [
    get_today,
    get_projects,
    get_versions,
    get_issues,
    get_project_metrics,

    create_version,
    update_version_dates,
]

CREATE_VERSION_SCHEMA = {
    "type": "object",
    "properties": {
        "project_id": {"type": "string", "title": "Project"},
        "name": {"type": "string", "title": "Name"},
        "due_date": {"type": "string", "title": "Due date"},
        "description": {"type": "string", "title": "Description"},
        "status": {"type": "string", "title": "Status"},
    },
    "required": ["project_id", "name"],
}

UPDATE_VERSION_SCHEMA = {
    "type": "object",
    "properties": {
        "version_id": {"type": "string", "title": "Version"},
        "due_date": {"type": "string", "title": "Due date"},
        "name": {"type": "string", "title": "Name"},
        "status": {"type": "string", "title": "Status"},
        "description": {"type": "string", "title": "Description"},
    },
    "required": ["version_id"],
}

interrupt_on = {
    "create_version":
        {"allowed_decisions": ["approve", "reject", "edit"], "description": "Review the version details before creating the sprint or milestone.", "args_schema": CREATE_VERSION_SCHEMA
        },
    
    "update_version_dates":
        {"allowed_decisions": ["approve", "reject", "edit"], "description": "Review the version update before saving changes.", "args_schema": UPDATE_VERSION_SCHEMA
        }
    }

def create_planning_agent(llm: ChatOpenAI):
    """
    Creates and returns the Planning ReAct agent.
    Handles: sprint status, milestone tracking, deadline analysis,
             sprint risk assessment, and sprint write operations.
    """

    PLANNING_LOCAL_RULES = """
Version and sprint handling rules:
- Treat sprint, version, and milestone as the same planning concept.
- When the user asks to create a sprint/version/milestone, always use create_version.
- When the user asks to rename, reschedule, lock, or otherwise update a sprint/version/milestone, always use update_version_dates.
- Do not refuse these requests in prose if the required write tool is available.
- These write tools are human-reviewed, so calling them should surface the approval dialog.
- If the project is unclear, ask a concise clarification before creating or updating anything.
""".strip()

    try:
        compiled_prompt = Langfuse().get_prompt("planning_agent", label="production").compile()
        PLANNING_PROMPT = "\n".join(
            m["content"] for m in compiled_prompt if m.get("role") == "system"
        )
        PLANNING_PROMPT = f"{PLANNING_PROMPT}\n\n{PLANNING_LOCAL_RULES}"
    except Exception as e:
        print("Error loading prompt from Langfuse:", e)
        raise

    return create_agent(
        model=llm,
        tools=tools,
        name="planning_agent",
        system_prompt=PLANNING_PROMPT,
        middleware=[
            HumanInTheLoopMiddleware(interrupt_on=interrupt_on)
            ]
    )   