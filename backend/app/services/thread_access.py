from fastapi import HTTPException, status
from psycopg import Connection

from app.repositories.thread_repository import ThreadRepository


def ensure_thread_owner(db: Connection, thread_id: str, user_id: str) -> None:
    if not thread_id.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="thread_id is required")

    threads = ThreadRepository(db)
    owner = threads.get_owner(thread_id)
    if owner is None:
        threads.bind_owner_if_missing(thread_id, user_id)
        return
    if owner != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your conversation",
        )
