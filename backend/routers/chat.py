from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any
import json

from agent.supervisor import chat, chat_stream, get_app
from langchain_core.messages import HumanMessage
from langgraph.types import Command

router = APIRouter(prefix="/api", tags=["chat"])


# ── Request / Response Models ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    requires_human: bool = False
    interrupts: Dict[str, Any] = {}


class ApproveRequest(BaseModel):
    decision_type: str = "approve"   # "approve" or "reject"
    message: str = ""                # optional feedback on reject


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint.
    Sends a message to the supervisor and returns the final response.
    If a write operation is pending confirmation, returns requires_human=True.
    """
    app    = get_app()
    config = {"configurable": {"thread_id": request.thread_id}}

    try:
        result = app.invoke(
            {"messages": [HumanMessage(content=request.message)]},
            config=config
        )

        # Check for HITL interrupt (write operation pending confirmation)
        if hasattr(result, "interrupts") and result.interrupts:
            pending = result.interrupts[0].value
            return ChatResponse(
                response="Action en attente de confirmation.",
                requires_human=True,
                interrupts=pending
            )

        response_msg = result["messages"][-1].content
        return ChatResponse(response=response_msg)

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
    """
    Resume execution after a write operation confirmation.

    POST /api/chat/approve/my-thread
    Body: {"decision_type": "approve"} or {"decision_type": "reject", "message": "Too risky"}
    """
    app    = get_app()
    config = {"configurable": {"thread_id": thread_id}}

    try:
        decision = {"type": request.decision_type}
        if request.decision_type == "reject" and request.message:
            decision["message"] = request.message

        result = app.invoke(
            Command(resume={"decisions": [decision]}),
            config=config
        )

        response_msg = result["messages"][-1].content
        return {
            "status":   request.decision_type,
            "response": response_msg
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}