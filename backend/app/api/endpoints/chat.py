from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from psycopg import Connection
from pydantic import BaseModel, Field, model_validator
from typing import Dict, Any, Literal, Optional
import json

from app.agent.supervisor import (
    chat_stream, 
    get_app, 
    chat_with_interrupts, 
    build_invoke_config,
    delete_thread_memory
)
from langgraph.types import Command

from app.dependencies.auth import CurrentUser, require_permission
from app.core.rbac import Permission
from app.repositories.thread_repository import ThreadRepository
from app.dependencies.db import get_db
from app.core.rbac import Role

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"


class CreateThreadResponse(BaseModel):
    thread_id: str


class ThreadSummary(BaseModel):
    id: str
    title: str
    preview: str
    updatedAt: float


class ThreadMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: int


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

    # Walk backward and pick the latest AI/assistant message only.
    for message in reversed(messages):
        mtype = type(message).__name__.lower()
        role = str(getattr(message, "type", "")).lower()

        is_tool = "toolmessage" in mtype or role == "tool"
        is_ai = ("aimessage" in mtype) or (role in {"ai", "assistant"})

        if is_tool:
            continue

        if is_ai:
            text = _message_content_to_text(message)
            if text:
                return text

    # Fallback: last non-tool message
    for message in reversed(messages):
        mtype = type(message).__name__.lower()
        if "toolmessage" in mtype:
            continue
        text = _message_content_to_text(message)
        if text:
            return text

    return "No response message produced."


def _raise_http_from_exception(exc: Exception) -> None:
    message = str(exc)

    if message.startswith("REDMINE_UNAVAILABLE:"):
        raise HTTPException(status_code=503, detail=message)

    if message.startswith("REDMINE_API_ERROR:"):
        raise HTTPException(status_code=502, detail=message)

    raise HTTPException(status_code=500, detail=message)


def _extract_thread_messages(state: Any) -> list[ThreadMessage]:
    payload = state.values if hasattr(state, "values") else state

    if isinstance(payload, dict):
        raw_messages = payload.get("messages", [])
    else:
        raw_messages = getattr(payload, "messages", [])

    extracted: list[ThreadMessage] = []
    for idx, message in enumerate(raw_messages):
        mtype = type(message).__name__.lower()
        role = str(getattr(message, "type", "")).lower()

        is_tool = "toolmessage" in mtype or role == "tool"
        if is_tool:
            continue

        is_assistant = "aimessage" in mtype or role in {"ai", "assistant"}
        is_user = "humanmessage" in mtype or role in {"human", "user"}

        if is_assistant:
            normalized_role: Literal["user", "assistant"] = "assistant"
        elif is_user:
            normalized_role = "user"
        else:
            continue

        text = _message_content_to_text(message)
        if not text:
            continue

        extracted.append(
            ThreadMessage(
                role=normalized_role,
                content=text,
                timestamp=idx,
            )
        )

    return extracted


def _enforce_thread_access(
        repo: ThreadRepository,
        thread_id: str,
        current_user: CurrentUser,
) -> None:
    repo.ensure_table()
    owner_id = repo.get_owner(thread_id)

    if owner_id is None:
        raise HTTPException(status_code=404, detail="Thread ownership not found")
    if current_user.role != Role.ADMIN and owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: thread does not belong to current user")


def _attach_user_identity_context(message: str, current_user: CurrentUser) -> str:
    identity_block = (
        "Authenticated user context:\n"
        f"- username: {current_user.username}\n"
        f"- full_name: {current_user.full_name or 'Unknown'}\n"
        f"- platform_user_id: {current_user.id}\n"
        f"- redmine_user_id: {current_user.redmine_user_id}\n"
        f"- platform_role: {current_user.role.value}\n"
        "Use this identity context for all references like 'me', 'my', 'mine', or 'our'."
    )
    return f"{identity_block}\n\nUser request:\n{message}"


@router.post("/chat/thread", response_model=CreateThreadResponse)
async def create_thread_endpoint(
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_db),
):
    thread_repo = ThreadRepository(db)
    thread_repo.ensure_table()
    thread_id = thread_repo.create_thread(current.id)
    return CreateThreadResponse(thread_id=thread_id)


@router.get("/chat/threads", response_model=list[ThreadSummary])
async def list_threads_endpoint(
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_db),
):
    thread_repo = ThreadRepository(db)
    thread_repo.ensure_table()
    items = thread_repo.list_threads_for_owner(current.id)
    return [ThreadSummary(**item) for item in items]


@router.get("/chat/thread/{thread_id}/messages", response_model=list[ThreadMessage])
async def get_thread_messages_endpoint(
    thread_id: str,
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_db),
):
    thread_repo = ThreadRepository(db)
    _enforce_thread_access(thread_repo, thread_id, current)

    app = get_app()
    config = build_invoke_config(thread_id=thread_id, entrypoint="history")

    try:
        state = app.get_state(config)
        return _extract_thread_messages(state)
    except Exception as e:
        _raise_http_from_exception(e)

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_db)
):
    thread_repo = ThreadRepository(db)
    _enforce_thread_access(thread_repo, request.thread_id, current)

    try:
        enriched_message = _attach_user_identity_context(request.message, current)
        result = chat_with_interrupts(enriched_message, request.thread_id)

        interrupts = result["interrupts"]
        if interrupts:
            pending = _interrupt_to_payload(interrupts[0])

            return ChatResponse(
                response="Action waiting for human confirmation.",
                requires_human=True,
                interrupts=pending
            )

        thread_repo.update_thread_summary(
            request.thread_id,
            title=request.message[:42].strip() or "New conversation",
            preview=result["response"][:70].strip() or "No messages yet",
        )
        return ChatResponse(response=result["response"])

    except Exception as e:
        _raise_http_from_exception(e)


@router.post("/chat/stream")
async def chat_stream_endpoint(
    request: ChatRequest,
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_db)
):
    thread_repo = ThreadRepository(db)
    _enforce_thread_access(thread_repo, request.thread_id, current)

    """
    Streaming chat endpoint using Server-Sent Events.
    Streams the agent's thought process step by step.
    """
    def event_generator():
        enriched_message = _attach_user_identity_context(request.message, current)
        for event in chat_stream(enriched_message, request.thread_id):
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
async def approve_endpoint(
    thread_id: str, 
    request: ApproveRequest,
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_db)
):
    thread_repo = ThreadRepository(db)
    _enforce_thread_access(thread_repo, thread_id, current)

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

        thread_repo.update_thread_summary(
            thread_id,
            title=f"Conversation {thread_id[:8]}",
            preview=_extract_full_message_content(result)[:70],
        )

        return {
            "status": request.decision_type,
            "response": _extract_full_message_content(result)
        }

    except Exception as e:
        _raise_http_from_exception(e)

@router.delete("/chat/thread/{thread_id}")
async def delete_thread_endpoint(
    thread_id: str,
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_db)
):
    thread_repo = ThreadRepository(db)
    _enforce_thread_access(thread_repo, thread_id, current)

    """Delete a thread's entire checkpoint history from PostgreSQL."""
    try:
        print(f"🗑️ Delete endpoint called for thread: {thread_id}")
        delete_thread_memory(thread_id)
        thread_repo.delete_thread(thread_id)
        print(f"✅ Successfully deleted thread: {thread_id}")
        return {
            "status": "deleted",
            "thread_id": thread_id,
            "message": f"Thread {thread_id} checkpoint purged from database"
        }
    except Exception as e:
        print(f"❌ Delete failed for thread {thread_id}: {e}")
        _raise_http_from_exception(e)

@router.get("/chat/thread/{thread_id}/exists")
async def check_thread_endpoint(
    thread_id: str,
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_db)
):
    thread_repo = ThreadRepository(db)
    _enforce_thread_access(thread_repo, thread_id, current)
    """Diagnostic endpoint: Check if a thread has checkpoints in PostgreSQL."""
    import os
    import psycopg
    
    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        raise HTTPException(status_code=500, detail="POSTGRES_URL not configured")
    
    try:
        with psycopg.connect(postgres_url) as conn:
            with conn.cursor() as cur:
                # Query the checkpoints table to see if thread exists
                cur.execute(
                    """
                    SELECT COUNT(*) FROM checkpoints 
                    WHERE thread_id = %s
                    """,
                    (thread_id,)
                )
                count = cur.fetchone()[0]
                
                return {
                    "thread_id": thread_id,
                    "exists": count > 0,
                    "checkpoint_count": count,
                    "message": f"Thread has {count} checkpoint(s)" if count > 0 
                            else "Thread has no checkpoints"
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")