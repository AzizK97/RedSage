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

from langfuse import get_client, Langfuse
from langfuse.langchain import CallbackHandler

import mlflow
from openai import OpenAI

load_dotenv()

#------- MLflow setup -------

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

#------- LangFuse setup -------

langfuse = Langfuse()

_langfuse_handler = None

def get_langfuse_handler():
    global _langfuse_handler
    if _langfuse_handler is not None:
        return _langfuse_handler

    try:
        # This initializes the global client using environment variables
        get_client()   # Ensures Langfuse client is set up with your keys

        _langfuse_handler = CallbackHandler()   # ← NO arguments!
        return _langfuse_handler
    except Exception as e:
        print(f"⚠️ Failed to initialize LangFuse: {e}")
        return None

def build_invoke_config(thread_id: str, entrypoint: str = "chat") -> dict:
    config: dict = {
        "configurable": {"thread_id": thread_id},
        "metadata": {
            "thread_id": thread_id,
            "entrypoint": entrypoint,
            "app": "redmine-agent",
        },
        "tags": ["redmine", "agent"],
    }

    handler = get_langfuse_handler()
    if handler:
        config["callbacks"] = [handler]

    return config

# def create_llm() -> ChatOllama:
#     return ChatOllama(
#         model="gemma4:e4b-it-q4_K_M",
#         temperature=0
#     )

def create_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("MODEL_NAME", "openrouter/auto"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0,
        max_tokens=700
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

    try:
        compiled_prompt = Langfuse().get_prompt("supervisor", label="production").compile()
        SUPERVISOR_PROMPT = "\n".join(
            m["content"] for m in compiled_prompt if m.get("role") == "system"
        )
    except Exception as e:
        print("Error loading prompt from Langfuse:", e)
        raise

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

    ignored_texts = {
        "transferring back to supervisor",
        "returning to supervisor",
        "back to supervisor",
        "transfer_to_report_agent",
        "transfer_to_overview_agent",
        "transfer_to_tasks_agent",
        "transfer_to_planning_agent",
    }

    def message_to_text(message: Any) -> str:
        content = getattr(message, "content", message)

        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text") or item.get("content") or ""
                    if text:
                        parts.append(str(text))
                elif item is not None:
                    parts.append(str(item))
            return "\n".join(part for part in parts if part).strip()

        if content is None:
            return ""

        return str(content).strip()

    # Return only the latest AI/assistant message from the current state,
    # skipping tool and supervisor transfer chatter.
    for message in reversed(messages):
        message_type = type(message).__name__.lower()
        role = str(getattr(message, "type", "")).lower()

        is_tool = "toolmessage" in message_type or role == "tool"
        if is_tool:
            continue

        is_ai = "aimessage" in message_type or role in {"ai", "assistant"}
        if not is_ai:
            continue

        text = message_to_text(message)
        if text and text.strip().lower() not in ignored_texts:
            return text

    # Fallback to latest non-tool message if no assistant message found.
    for message in reversed(messages):
        message_type = type(message).__name__.lower()
        role = str(getattr(message, "type", "")).lower()
        if "toolmessage" in message_type or role == "tool":
            continue
        text = message_to_text(message)
        if text:
            return text

    return "No response message produced."


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