from fastapi import APIRouter, Depends
from psycopg import Connection

from app.dependencies.auth import CurrentUser, require_permission
from app.core.rbac import Permission
from app.dependencies.db import get_agent_db
from app.repositories.thread_repository import ThreadRepository

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search")
def search_endpoint(
    q: str,
    limit: int = 20,
    offset: int = 0,
    current: CurrentUser = Depends(require_permission(Permission.CHAT_USE)),
    db: Connection = Depends(get_agent_db),
):
    """Search conversation threads by title for the current user."""
    repo = ThreadRepository(db)
    repo.ensure_table()
    result = repo.search_threads_for_user(
        query=q,
        owner_user_id=current.id,
        limit=limit,
        offset=offset,
    )
    return result
