from langchain.agents import create_agent
from langchain_openai import ChatOpenAI


def create_notification_summary_agent(llm: ChatOpenAI):
    """Create a dedicated agent for monitoring digest summaries."""
    system_prompt = (
        "You are a monitoring summary agent for project management teams.\n"
        "Write concise Slack digests that are clear and actionable.\n"
        "Output plain text with this style:\n"
        "- one short title line\n"
        "- then 3 to 5 short bullets\n"
        "- include momentum, risk, overdue, and one action item\n"
        "- keep language simple and professional\n"
        "- no markdown tables and no hallucinated metrics.\n"
    )

    return create_agent(
        model=llm,
        tools=[],
        name="notification_summary_agent",
        system_prompt=system_prompt,
    )
