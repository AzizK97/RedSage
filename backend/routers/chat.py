from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, model_validator
from typing import Dict, Any, Literal, Optional
import json

from agent.supervisor import chat_stream, get_app
from langchain_core.messages import HumanMessage
from langgraph.types import Command

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    requires_human: bool = False
    interrupts: Dict[str, Any] = Field(default_factory=dict)


class ApproveRequest(BaseModel):
    decision_type: Literal["approve", "reject", "edit"] = "approve"
    message: str = ""                
    edited_action: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def validate_edit_payload(self):
        if self.decision_type == "edit":
            
            if not self.edited_action:
                raise ValueError("edited_action is required when decision_type is 'edit'")
            
            if "name" not in self.edited_action or "args" not in self.edited_action:
                raise ValueError("edited_action must contain 'name' and 'args'")
            
            if not isinstance(self.edited_action["args"], dict):
                raise ValueError("edited_action 'args' must be a dictionary")
            
        return self

def _extract_interrupts(result: Any) -> list[Any]:

    if hasattr(result, "interrupts") and getattr(result, "interrupts", None):
        return list(result.interrupts)
    
    if isinstance(result, dict):
        legacy = result.get("__interrupt__")
        if legacy:
            return list(legacy)
        
    return []
    
def _interrupt_to_payload(interrupt_obj: Any) -> Dict[str, Any]:
    if hasattr(interrupt_obj, "value"):
        value = interrupt_obj.value
        return value if isinstance(value, dict) else {"value": value}
    
    if isinstance(interrupt_obj, dict):
        value = interrupt_obj.get("value", interrupt_obj)
        return value if isinstance(value, dict) else {"value": value}
    
    return {"value": interrupt_obj}

def _extract_last_message_content(result: Any) -> str:
    payload = result.value if hasattr(result, "value") else result

    if isinstance(payload, dict):
        messages = payload.get("messages", [])
    else:
        messages = getattr(payload, "messages", [])

    if not messages:
        return "No response message produced."
    
    last = messages[-1]

    return getattr(last, "content", str(last))


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    app = get_app()
    config = {"configurable": {"thread_id": request.thread_id}}

    try:
        result = app.invoke(
            {"messages": [HumanMessage(content=request.message)]},
            config=config
        )

        interrupts = _extract_interrupts(result)
        if interrupts:
            pending = _interrupt_to_payload(interrupts[0])

            return ChatResponse(
                response="Action waiting for human confirmation.",
                requires_human=True,
                interrupts=pending
            )

        return ChatResponse(response=_extract_last_message_content(result))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint using Server-Sent Events.
    Streams the agent's thought process step by step.
    """
    def event_generator():
        for event in chat_stream(request.message, request.thread_id):
            yield f"data: {json.dumps(event)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/chat/approve/{thread_id}")
async def approve_endpoint(thread_id: str, request: ApproveRequest):
    app = get_app()
    config = {"configurable": {"thread_id": thread_id}}

    try:
        if request.decision_type == "edit":
            decision = {
                "type": "edit",
                "edited_action": request.edited_action
            }

        elif request.decision_type == "reject":
            decision = {"type": "reject"}    
            if request.message:
                decision["message"] = request.message

        else:
            decision = {"type": "approve"}

        result = app.invoke(
            Command(resume={"decisions": [decision]}),
            config=config
        )

        return {
            "status": request.decision_type,
            "response": _extract_last_message_content(result)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}