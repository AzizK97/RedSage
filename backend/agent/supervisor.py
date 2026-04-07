import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph_supervisor import create_supervisor
from typing import Any

from agent.agents.overview  import create_overview_agent
from agent.agents.tasks     import create_tasks_agent
from agent.agents.planning  import create_planning_agent
from agent.agents.report    import create_report_agent

import mlflow
from openai import OpenAI

load_dotenv()

def build_invoke_config(thread_id: str, entrypoint: str = "chat") -> dict:
    """Build invoke config with thread_id and request metadata."""
    config: dict = {
        "configurable": {"thread_id": thread_id},
        "metadata":{
            "thread_id": thread_id,
            "entrypoint": entrypoint,
            "app": "redmine_agent",           
        },
        "tags": ["redmine", "agent"],
    }

    return config

# Specify the tracking URI for the MLflow server.
mlflow.set_tracking_uri("http://localhost:5000")

# Specify the experiment you just created for your LLM application or AI agent.
mlflow.set_experiment("Redmine Agent")

# Enable automatic tracing for all OpenAI API calls.
mlflow.openai.autolog()

client = OpenAI(
    base_url=os.getenv("https://openrouter.ai/api/v1"),
    api_key=os.getenv("OPENROUTER_API_KEY")
)


SUPERVISOR_PROMPT = """You are an intelligent supervisor of a multi-agent Redmine project management system.
You analyze the user's question and delegate it to the most appropriate specialized agent.

Available agents:

- overview_agent: General questions about projects — summary, team, overall status
  Examples: "What projects exist?", "Tell me about project X"
- tasks_agent: Everything related to tasks — listing, filtering, workload,
  AND all write operations on tasks (create, close, reassign, comment, log time)
  Examples: "Overdue tasks", "Create a ticket", "Close issue #5"
- planning_agent: Sprints, milestones, deadlines, planning risks,
  AND creation/modification of sprints
  Examples: "Progress of Sprint 2", "Create Sprint 4", "At-risk sprints"
- report_agent: Complete health reports covering all aspects of a project
  Examples: "Full report", "How is the project doing?"

ROUTING RULES:

1. ALWAYS delegate to exactly one agent — never respond yourself.
2. For mixed questions (e.g. tasks + sprints), prioritize tasks_agent.
3. For any report or global synthesis, use report_agent.
4. For any write operation (create, modify, close...), use tasks_agent (for tasks) or planning_agent (for sprints).
5. In case of doubt, use overview_agent.
6. Delegate once.
7. After receiving delegated agent result, return it and end turn.
8. DO NOT re-delegate in same turn.
9. DO NOT append generic follow-up text.
10. If a sprint id is not provided for issues creation, or the reverse, return to the overview agent to resolve the missing identifier before routing to the final agent.
11. Once a sub-agent returns a final answer containing a markdown report or markdown table, return it immediately to the user without re-delegating or paraphrasing it away.
12. For sprint/version list questions, ensure the final response contains the actual list data, not a vague summary.
13. You can reply in either French or English, depending on the language used in the user's prompt.
"""

# def create_llm() -> ChatOllama:
#     return ChatOllama(
#         model="gemma4:e4b-it-q4_K_M",
#         temperature=0
#     )

def create_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model="openrouter/auto",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0,
        max_tokens=3000
    )

def create_app():
    """
    Build and compile the full supervisor multi-agent application.
    Returns a compiled LangGraph app ready to invoke.
    """
    llm = create_llm()
    overview_agent  = create_overview_agent(llm)
    tasks_agent     = create_tasks_agent(llm)
    planning_agent  = create_planning_agent(llm)
    report_agent    = create_report_agent(llm)

    workflow = create_supervisor(
        [overview_agent, tasks_agent, planning_agent, report_agent],
        model=llm,
        prompt=SUPERVISOR_PROMPT,
        output_mode="last_message" 
    )
    memory = InMemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app

_app = None

# Singleton pattern to reuse the same app instance across requests
def get_app():
    global _app
    if _app is None:
        _app = create_app()
    return _app


def _invoke_chat(question: str, thread_id: str) -> Any:
    app = get_app()
    config = build_invoke_config(thread_id=thread_id, entrypoint="chat")

    return app.invoke(
        {"messages": [HumanMessage(content=question)]},
        config=config
    )


def extract_final_message_content(result: Any) -> str:
    """
    Extract the user-facing assistant text from a LangGraph result.

    This skips tool messages and routing/transfer messages so callers do not
    accidentally display internal supervisor chatter.
    """
    payload = result.value if hasattr(result, "value") else result

    if isinstance(payload, dict):
        messages = payload.get("messages", [])
    else:
        messages = getattr(payload, "messages", [])

    if not messages:
        return "No response message produced."

    text_blocks: list[str] = []
    seen: set[str] = set()

    for message in messages:
        message_type = type(message).__name__.lower()

        if "aimessage" not in message_type:
            continue

        if "toolmessage" in message_type:
            continue

        content = getattr(message, "content", message)
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text") or item.get("content") or ""
                    if text:
                        parts.append(str(text))
                elif item is not None:
                    parts.append(str(item))
            text = "\n".join(part for part in parts if part).strip()
        elif content is None:
            text = ""
        else:
            text = str(content).strip()

        if not text or text in seen:
            continue

        seen.add(text)
        text_blocks.append(text)

    if not text_blocks:
        last = messages[-1]
        return str(getattr(last, "content", last)).strip()

    filtered_blocks = [
        block for block in text_blocks
        if block.strip().lower() not in {
            "transferring back to supervisor",
            "returning to supervisor",
            "back to supervisor",
            "transfer_to_report_agent",
            "transfer_to_overview_agent",
            "transfer_to_tasks_agent",
            "transfer_to_planning_agent",
        }
    ]

    return "\n\n".join(filtered_blocks or text_blocks)


def chat(question: str, thread_id: str = "default") -> str:
    """
    Send a message to the supervisor and return the final response.

    Args:
        question:  User's natural language question
        thread_id: Conversation thread ID for memory persistence
    """
    result = _invoke_chat(question, thread_id)
    return extract_final_message_content(result)


def chat_with_interrupts(question: str, thread_id: str = "default") -> dict[str, Any]:
    """
    Send a message to the supervisor and return the raw result with a parsed
    assistant response plus any pending interrupts.
    """
    result = _invoke_chat(question, thread_id)

    messages = result["messages"]
    interrupts: Any = []
    if hasattr(result, "interrupts") and getattr(result, "interrupts", None):
        interrupts = getattr(result, "interrupts")
    elif isinstance(result, dict):
        interrupts = result.get("__interrupt__", [])

    return {
        "result": result,
        "response": extract_final_message_content(result),
        "interrupts": list(interrupts) if interrupts else [],
    }


def chat_stream(question: str, thread_id: str = "default"):
    """
    Stream the supervisor's response step by step.
    Yields dicts with keys: type, agent, content.

    Yield types:
        - "routing"  : supervisor decided which agent to call
        - "thinking" : agent is reasoning / calling a tool
        - "answer"   : final response from the agent
        - "error"    : something went wrong
    """
    app    = get_app()
    config = build_invoke_config(thread_id=thread_id, entrypoint="chat_stream")

    try:
        for step in app.stream(
            {"messages": [HumanMessage(content=question)]},
            config=config,
            stream_mode="updates"
        ):
            for node_name, node_data in step.items():
                messages = node_data.get("messages", [])
                for message in messages:
                    from langchain_core.messages import AIMessage, ToolMessage

                    if isinstance(message, AIMessage) and message.tool_calls:
                        yield {
                            "type":    "thinking",
                            "agent":   node_name,
                            "content": f"Calling tool: {message.tool_calls[0]['name']}"
                        }

                    elif isinstance(message, ToolMessage):
                        yield {
                            "type":    "thinking",
                            "agent":   node_name,
                            "content": f"Tool result received"
                        }

                    elif isinstance(message, AIMessage) and message.content:
                        # Detect if this is the supervisor routing or a final answer
                        if node_name == "supervisor":
                            yield {
                                "type":    "routing",
                                "agent":   node_name,
                                "content": message.content
                            }
                        else:
                            yield {
                                "type":    "answer",
                                "agent":   node_name,
                                "content": message.content
                            }
    except Exception as e:
        yield {
            "type":    "error",
            "agent":   "supervisor",
            "content": str(e)
        }


if __name__ == "__main__":
    print("=== Redmine Supervisor Agent ===")
    print("Type 'exit' to quit\n")

    thread_id = "cli-session-1"

    while True:
        question = input("You : ").strip()
        if not question:
            continue
        if question.lower() == "exit":
            print("Bye!")
            break

        print("\nAgent :")
        final_answer = None

        for event in chat_stream(question, thread_id):
            etype = event.get("type")
            content = (event.get("content") or "").strip()

            if not content:
                continue

            if etype == "routing":
                print(f"[routing] {content}")
            elif etype == "thinking":
                print(f"[tool] {content}")
            elif etype == "answer":
                final_answer = content
            elif etype == "error":
                print(f"[error] {content}")

        if final_answer:
            print(f"\nFinal: {final_answer}\n")
        else:
            print("\nFinal: No final text answer generated.\n")