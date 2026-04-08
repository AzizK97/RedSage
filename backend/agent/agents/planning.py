from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from agent.tools.read import get_projects, get_versions, get_issues
from agent.tools.write import create_version, update_version_dates
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langfuse import get_client, Langfuse

tools = [
            
            get_projects,
            get_versions,
            get_issues,

            create_version,
            update_version_dates
        ]

interrupt_on = {
    "create_version":
        {"allowed_decisions": 
            ["approve","reject"]
        },
    
    "update_version_dates":
        {"allowed_decisions":
            ["approve","reject"]
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