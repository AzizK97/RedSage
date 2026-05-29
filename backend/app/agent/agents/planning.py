from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from app.agent.tools.read import get_today, get_projects, get_versions, get_issues, get_project_metrics
from app.agent.tools.write import create_version, update_version_dates
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langfuse import get_client, Langfuse

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

    try:
        compiled_prompt = Langfuse().get_prompt("planning_agent", label="production").compile()
        PLANNING_PROMPT = "\n".join(
            m["content"] for m in compiled_prompt if m.get("role") == "system"
        )
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