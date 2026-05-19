from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from app.agent.tools.read import get_projects, get_issues, get_members, get_issue_detail
from app.agent.tools.write import (
    create_issue,
    update_issue_status,
    reassign_issue,
    add_comment_to_issue,
    update_issue_dates,
    log_time
)
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langfuse import Langfuse

tools = [
            get_projects,
            get_issues,
            get_members,
            get_issue_detail,
            
            create_issue,
            update_issue_status,
            reassign_issue,
            add_comment_to_issue,
            update_issue_dates,
            log_time
        ]

interrupt_on = {
    "create_issue":
        {"allowed_decisions": 
            ["approve","reject","edit"]
        },
    
    "update_issue_status":
        {"allowed_decisions":
            ["approve","reject","edit"]
        },
    
    "reassign_issue":
        {"allowed_decisions":
            ["approve","reject","edit"]
        },
    
    "add_comment_to_issue":
        {"allowed_decisions":
            ["approve","reject","edit"]
        },
    
    "update_issue_dates":
        {"allowed_decisions":
            ["approve","reject","edit"]
        },
    
    "log_time":
        {"allowed_decisions":
            ["approve","reject","edit"]
        }
    }

def create_tasks_agent(llm: ChatOpenAI):
    """
    Creates and returns the Tasks ReAct agent.
    Handles: task listing, filtering, workload analysis,
             and all write operations on issues.
    """
    try:
        compiled_prompt = Langfuse().get_prompt("tasks_agent", label="latest").compile()
        TASKS_PROMPT = "\n".join(
            m["content"] for m in compiled_prompt if m.get("role") == "system"
        )
    except Exception as e:
        print("Error loading prompt from Langfuse:", e)
        raise

    return create_agent(
        model=llm,
        tools=tools,
        name="tasks_agent",
        system_prompt=TASKS_PROMPT,
        middleware=[
            HumanInTheLoopMiddleware(interrupt_on=interrupt_on)
            ]
    )