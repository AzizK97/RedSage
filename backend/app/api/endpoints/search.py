from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Literal
from psycopg import Connection

from app.dependencies.auth import CurrentUser, require_permission
from app.core.rbac import Permission, Role
from app.dependencies.db import get_db, get_agent_db
from app.repositories.thread_message_repository import ThreadMessageRepository
from app.repositories.thread_repository import ThreadRepository
from app.agent.cache import get_cached_sync
from app.agent.tools.read import set_session_user

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search")
def search_endpoint(
    q: str,
    type: Literal["messages", "threads"] = "messages",
    limit: int = 20,
    offset: int = 0,
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_agent_db),
):
    """Search messages or threads. Results are restricted by the caller's allowed projects (PMs).

    Returns JSON with keys: total, items
    """
    # Ensure allowed projects are cached/populated for this user
    is_admin = (current.role == Role.ADMIN)
    try:
        set_session_user(current.redmine_user_id, is_admin=is_admin)
    except Exception:
        # If session setup fails, fall back to cache lookup only
        pass

    cache_key = f"allowed_projects:{current.redmine_user_id}"
    allowed = get_cached_sync(cache_key)

    if is_admin:
        allowed = None

    if type == "messages":
        repo = ThreadMessageRepository(db)
        repo.ensure_table()
        result = repo.search_messages(q, allowed, limit=limit, offset=offset)
        return result

    else:
        repo = ThreadRepository(db)
        repo.ensure_table()
        result = repo.search_threads(q, allowed, limit=limit, offset=offset)
        return result
