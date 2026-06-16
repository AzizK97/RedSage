from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, model_validator
from typing import Dict, Any, List, Literal, Optional
import json
import os
import re
import psycopg

from psycopg import Connection
from langgraph.types import Command

from app.agent.supervisor import (
    chat_stream,
    get_app,
    chat_with_interrupts,
    build_invoke_config,
    delete_thread_memory,
)
from app.agent.tools.read import set_session_user, clear_session_user
from app.core.rbac import Permission, Role
from app.dependencies.auth import CurrentUser, require_permission
from app.dependencies.db import get_db, get_agent_db
from app.repositories.thread_message_repository import ThreadMessageRepository
from app.repositories.thread_repository import ThreadRepository
from app.services.chat_persistence import (
    ensure_thread_tables,
    persist_assistant_only,
    persist_user_and_assistant,
)
from app.services.thread_access import ensure_thread_owner

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


class CreateThreadResponse(BaseModel):
    thread_id: str


class ThreadListItem(BaseModel):
    thread_id: str
    title: str
    preview: str
    updated_at: int


class RenameThreadRequest(BaseModel):
    title: str

    @model_validator(mode="after")
    def validate_title(self):
        if not self.title or not self.title.strip():
            raise ValueError("title cannot be empty")
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
        # A Redmine 4xx is a request/validation error (e.g. an invalid
        # version_id), not a gateway failure. Surface it as a 400 carrying
        # Redmine's own message instead of a misleading 502 Bad Gateway.
        # Genuine upstream failures (5xx) or unparseable errors stay 502.
        status_match = re.search(r"HTTP (\d{3})", message)
        if status_match and 400 <= int(status_match.group(1)) < 500:
            detail = message
            body_match = re.search(r"Response:\s*(\{.*\})", message)
            if body_match:
                try:
                    errors = json.loads(body_match.group(1)).get("errors")
                    if errors:
                        detail = "; ".join(str(e) for e in errors) if isinstance(errors, list) else str(errors)
                except Exception:
                    pass
            raise HTTPException(status_code=400, detail=detail)
        raise HTTPException(status_code=502, detail=message)

    if "human decisions" in message.lower() or "does not match num" in message.lower():
        raise HTTPException(
            status_code=409,
            detail=(
                "The approval state is out of sync with the backend checkpoint. "
                "Refresh the page and submit the currently visible approval again."
            ),
        )

    raise HTTPException(status_code=500, detail=message)


def _get_thread_pending_interrupt(db: Connection, thread_id: str) -> dict | None:
    return ThreadRepository(db).get_pending_interrupt(thread_id)


def _set_thread_pending_interrupt(db: Connection, thread_id: str, pending: dict | None) -> None:
    threads = ThreadRepository(db)
    if pending:
        threads.set_pending_interrupt(thread_id, pending)
    else:
        threads.clear_pending_interrupt(thread_id)


def _persist_pending_interrupt_fresh(thread_id: str, pending: dict | None) -> None:
    """Persist (or clear) a thread's pending interrupt on a dedicated connection.

    The streaming endpoint cannot reuse the request-scoped DB dependency from
    inside the StreamingResponse generator: that connection is torn down before
    the generator finishes, so writes there are silently lost. We therefore open
    a short-lived, autocommit connection just for this write.
    """
    url = os.getenv("POSTGRES_URL")
    if not url:
        return
    with psycopg.connect(url, autocommit=True) as conn:
        _set_thread_pending_interrupt(conn, thread_id, pending)


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_agent_db),
):
    ensure_thread_tables(db)
    ensure_thread_owner(db, request.thread_id, current.id)

    try:
        result = chat_with_interrupts(
            request.message,
            request.thread_id,
            redmine_user_id=current.redmine_user_id,
            is_admin=(current.role == Role.ADMIN),
        )

        interrupts = result["interrupts"]
        if interrupts:
            pending = _interrupt_to_payload(interrupts[0])
            persist_user_and_assistant(
                db,
                request.thread_id,
                request.message,
                "Action waiting for human confirmation.",
            )
            _set_thread_pending_interrupt(db, request.thread_id, pending)
            return ChatResponse(
                response="Action waiting for human confirmation.",
                requires_human=True,
                interrupts=pending,
            )

        _set_thread_pending_interrupt(db, request.thread_id, None)
        persist_user_and_assistant(db, request.thread_id, request.message, result["response"])
        return ChatResponse(response=result["response"])

    except Exception as e:
        _raise_http_from_exception(e)


@router.post("/chat/stream")
async def chat_stream_endpoint(
    request: ChatRequest,
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_agent_db),
):
    """
    Streaming chat endpoint using Server-Sent Events.
    Streams the agent's thought process step by step.
    No server-side message persistence for this path (use POST /api/chat for durable history).
    """
    ensure_thread_tables(db)
    ensure_thread_owner(db, request.thread_id, current.id)

    def event_generator():
        saw_interrupt = False
        for event in chat_stream(
            request.message,
            request.thread_id,
            redmine_user_id=current.redmine_user_id,
            is_admin=(current.role == Role.ADMIN),
        ):
            # A human-in-the-loop approval was raised: persist it as the thread's
            # pending interrupt so the dialog can be resolved through
            # POST /chat/approve/{thread_id}, then forward it to the client.
            if event.get("type") == "interrupt":
                saw_interrupt = True
                try:
                    _persist_pending_interrupt_fresh(
                        request.thread_id, _interrupt_to_payload(event.get("value"))
                    )
                except Exception:
                    pass
            yield f"data: {json.dumps(event)}\n\n"

        # Clear any stale pending interrupt when the turn completed without one.
        if not saw_interrupt:
            try:
                _persist_pending_interrupt_fresh(request.thread_id, None)
            except Exception:
                pass
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/chat/approve/{thread_id}")
async def approve_endpoint(
    thread_id: str,
    request: ApproveRequest,
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_agent_db),
):
    app = get_app()
    config = build_invoke_config(thread_id=thread_id, entrypoint="chat_stream")
    ensure_thread_tables(db)
    ensure_thread_owner(db, thread_id, current.id)

    pending_interrupt = _get_thread_pending_interrupt(db, thread_id)
    if not pending_interrupt:
        # The DB column is only a UI convenience; the checkpoint is the real
        # source of truth for whether the graph is paused. Fall back to it so a
        # genuinely interrupted graph can still be resumed.
        try:
            snapshot = app.get_state(config)
            has_state_interrupt = bool(getattr(snapshot, "interrupts", None))
        except Exception:
            has_state_interrupt = False
        if not has_state_interrupt:
            raise HTTPException(
                status_code=409,
                detail=(
                    "No pending approval exists for this thread. Refresh the page and wait for a new approval request."
                ),
            )

    try:
        set_session_user(current.redmine_user_id, is_admin=(current.role == Role.ADMIN))

        if request.decision_type == "edit":
            decision = {
                "type": "edit",
                "edited_action": request.edited_action,
            }
        elif request.decision_type == "reject":
            decision = {"type": "reject"}
            if request.message:
                decision["message"] = request.message
        else:
            decision = {"type": "approve"}

        result = app.invoke(
            Command(resume={"decisions": [decision]}),
            config=config,
        )

        response_text = _extract_full_message_content(result)
        persist_assistant_only(db, thread_id, response_text)
        _set_thread_pending_interrupt(db, thread_id, None)
        return {
            "status": request.decision_type,
            "response": response_text,
        }

    except Exception as e:
        _raise_http_from_exception(e)
    finally:
        clear_session_user()


@router.delete("/chat/thread/{thread_id}")
async def delete_thread_endpoint(
    thread_id: str,
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_agent_db),
):
    """Delete a thread's entire checkpoint history from PostgreSQL."""
    ensure_thread_tables(db)
    ensure_thread_owner(db, thread_id, current.id)
    try:
        print(f"🗑️ Delete endpoint called for thread: {thread_id}")
        delete_thread_memory(thread_id)
        ThreadRepository(db).delete_thread(thread_id)
        print(f"✅ Successfully deleted thread: {thread_id}")
        return {
            "status": "deleted",
            "thread_id": thread_id,
            "message": f"Thread {thread_id} checkpoint purged from database",
        }
    except Exception as e:
        print(f"❌ Delete failed for thread {thread_id}: {e}")
        _raise_http_from_exception(e)


@router.patch("/chat/thread/{thread_id}/rename")
async def rename_thread_endpoint(
    thread_id: str,
    request: RenameThreadRequest,
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_agent_db),
):
    """Rename a conversation thread."""
    ensure_thread_tables(db)
    ensure_thread_owner(db, thread_id, current.id)
    try:
        thread_repo = ThreadRepository(db)
        # Get current preview to keep it unchanged
        with db.cursor() as cur:
            cur.execute(
                "SELECT preview FROM thread_owners WHERE thread_id = %s",
                (thread_id,),
            )
            row = cur.fetchone()
            preview = row[0] if row else "No messages yet"
        
        # Update title
        thread_repo.update_metadata(thread_id, request.title.strip(), preview)
        return {
            "status": "renamed",
            "thread_id": thread_id,
            "title": request.title.strip(),
        }
    except Exception as e:
        print(f"❌ Rename failed for thread {thread_id}: {e}")
        _raise_http_from_exception(e)


@router.get("/chat/thread/{thread_id}/exists")
async def check_thread_endpoint(
    thread_id: str,
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_agent_db),
):
    """Diagnostic endpoint: Check if a thread has checkpoints in PostgreSQL."""
    ensure_thread_tables(db)
    ensure_thread_owner(db, thread_id, current.id)

    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        raise HTTPException(status_code=500, detail="POSTGRES_URL not configured")

    try:
        with psycopg.connect(postgres_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*) FROM checkpoints
                    WHERE thread_id = %s
                    """,
                    (thread_id,),
                )
                count = cur.fetchone()[0]

                return {
                    "thread_id": thread_id,
                    "exists": count > 0,
                    "checkpoint_count": count,
                    "message": f"Thread has {count} checkpoint(s)" if count > 0 else "Thread has no checkpoints",
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/chat/thread", response_model=CreateThreadResponse)
def create_thread_endpoint(
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_agent_db),
):
    ensure_thread_tables(db)
    thread_id = ThreadRepository(db).create_thread(current.id)
    return CreateThreadResponse(thread_id=thread_id)


@router.get("/chat/threads", response_model=List[ThreadListItem])
def list_threads_endpoint(
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_agent_db),
):
    ensure_thread_tables(db)
    rows = ThreadRepository(db).list_for_owner(current.id)
    return [
        ThreadListItem(
            thread_id=r["thread_id"],
            title=r["title"],
            preview=r["preview"],
            updated_at=r["updated_at_ms"],
        )
        for r in rows
    ]


@router.get("/chat/thread/{thread_id}/messages")
def get_thread_messages_endpoint(
    thread_id: str,
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_agent_db),
):
    ensure_thread_tables(db)
    ensure_thread_owner(db, thread_id, current.id)
    raw = ThreadMessageRepository(db).list_for_thread(thread_id)
    return {
        "messages": raw,
        "pending_interrupt": ThreadRepository(db).get_pending_interrupt(thread_id),
    }
