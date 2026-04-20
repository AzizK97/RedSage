from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from app.agent.tools.read import get_projects, get_issues, get_members, get_versions
from langfuse import Langfuse

tools = [get_projects, get_issues, get_members, get_versions]

def create_overview_agent(llm: ChatOpenAI):
    """
    Creates and returns the Overview ReAct agent.
    Handles: project summaries, team info, general project status.
    """

    try:
        compiled_prompt = Langfuse().get_prompt("overview_agent", label="production").compile()
        OVERVIEW_PROMPT = "\n".join(
            m["content"] for m in compiled_prompt if m.get("role") == "system"
        )
    except Exception as e:
        print("Error loading prompt from Langfuse:", e)
        raise

    return create_agent(
        model=llm,
        tools=tools,
        name="overview_agent",
        system_prompt=OVERVIEW_PROMPT
    )