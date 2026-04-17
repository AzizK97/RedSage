from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from app.agent.tools.read import get_projects, get_issues, get_members, get_versions
from langfuse import Langfuse

tools = [get_projects, get_issues, get_members, get_versions]

def create_report_agent(llm: ChatOpenAI):
    """
    Creates and returns the Report ReAct agent.
    Handles: full project health reports, KPI summaries,
             risk synthesis, and team status reports.
    """

    try:
        compiled_prompt = Langfuse().get_prompt("report_agent", label="production").compile()
        REPORT_PROMPT = "\n".join(
            m["content"] for m in compiled_prompt if m.get("role") == "system"
        )
    except Exception as e:
        print("Error loading prompt from Langfuse:", e)
        raise

    return create_agent(
        model=llm,
        tools=tools,
        name="report_agent",
        system_prompt=REPORT_PROMPT
    )