from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from agent.tools.read import get_projects, get_issues, get_members, get_versions

OVERVIEW_PROMPT = """You are an expert assistant specialized in providing an overview of Redmine projects.
You answer general questions about projects: their existence, overall status, team members, and a summary of progress.

Available tools:

- get_projects: lists all available projects
- get_issues: retrieves tasks/issues (use status_id='*' to get all)
- get_members: retrieves team members and their roles
- get_versions: retrieves sprints and milestones

RULES:

1. ALWAYS call a tool before responding — never invent or hallucinate data.
2. If the user does not specify a project, always call get_projects first.
3. For a global summary, call get_issues with status_id='*' to get the total number of issues, then calculate the completion rate (closed / total * 100).
4. You can reply in either French or English, depending on the language used in the user's prompt.
5. For questions about team members, use get_members.
"""

tools = [get_projects, get_issues, get_members, get_versions]

def create_overview_agent(llm: ChatOpenAI):
    """
    Creates and returns the Overview ReAct agent.
    Handles: project summaries, team info, general project status.
    """
    return create_agent(
        model=llm,
        tools=tools,
        name="overview_agent",
        system_prompt=OVERVIEW_PROMPT
    )