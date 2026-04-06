from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, model_validator
from typing import Dict, Any, Literal, Optional
import json

from agent.supervisor import chat_stream, get_app, chat_with_interrupts, build_invoke_config
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

def _interrupt_to_payload(interrupt_obj: Any) -> Dict[str, Any]:
    if hasattr(interrupt_obj, "value"):
        value = interrupt_obj.value
        return value if isinstance(value, dict) else {"value": value}
    
    if isinstance(interrupt_obj, dict):
        value = interrupt_obj.get("value", interrupt_obj)
        return value if isinstance(value, dict) else {"value": value}
    
    return {"value": interrupt_obj}

def _message_content_to_text(message: Any) -> str:
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
        return "\n".join(part for part in parts if part).strip()

    if content is None:
        return ""

    return str(content).strip()


def _extract_full_message_content(result: Any) -> str:
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
        if "toolmessage" in message_type:
            continue

        text = _message_content_to_text(message)
        if not text:
            continue

        if text not in seen:
            seen.add(text)
            text_blocks.append(text)

    if not text_blocks:
        last = messages[-1]
        return _message_content_to_text(last) or str(last)

    filtered_blocks = [
        block for block in text_blocks
        if block.strip().lower() not in {
            "transferring back to supervisor",
            "returning to supervisor",
            "back to supervisor",
        }
    ]

    return "\n\n".join(filtered_blocks or text_blocks)


def _raise_http_from_exception(exc: Exception) -> None:
    message = str(exc)

    if message.startswith("REDMINE_UNAVAILABLE:"):
        raise HTTPException(status_code=503, detail=message)

    if message.startswith("REDMINE_API_ERROR:"):
        raise HTTPException(status_code=502, detail=message)

    raise HTTPException(status_code=500, detail=message)


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        result = chat_with_interrupts(request.message, request.thread_id)

        interrupts = result["interrupts"]
        if interrupts:
            pending = _interrupt_to_payload(interrupts[0])

            return ChatResponse(
                response="Action waiting for human confirmation.",
                requires_human=True,
                interrupts=pending
            )

        return ChatResponse(response=result["response"])

    except Exception as e:
        _raise_http_from_exception(e)


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
    config = build_invoke_config(thread_id=thread_id, entrypoint="chat_stream")

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
            "response": _extract_full_message_content(result)
        }

    except Exception as e:
        _raise_http_from_exception(e)


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}