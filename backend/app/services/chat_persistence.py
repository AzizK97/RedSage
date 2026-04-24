from psycopg import Connection

from app.repositories.thread_message_repository import ThreadMessageRepository
from app.repositories.thread_repository import ThreadRepository


def _trim_title(text: str, max_len: int = 42) -> str:
    compact = " ".join(text.split()).strip()
    if not compact:
        return "New conversation"
    if len(compact) <= max_len:
        return compact
    return f"{compact[: max_len - 1]}…"


def _trim_preview(text: str, max_len: int = 70) -> str:
    compact = " ".join(text.split()).strip()
    if not compact:
        return "No messages yet"
    if len(compact) <= max_len:
        return compact
    return f"{compact[: max_len - 1]}…"


def ensure_thread_tables(db: Connection) -> None:
    ThreadRepository(db).ensure_table()
    ThreadMessageRepository(db).ensure_table()


def persist_user_and_assistant(
    db: Connection,
    thread_id: str,
    user_text: str,
    assistant_text: str,
) -> None:
    messages = ThreadMessageRepository(db)
    threads = ThreadRepository(db)
    messages.append(thread_id, "user", user_text)
    messages.append(thread_id, "assistant", assistant_text)
    title = _trim_title(user_text)
    preview = _trim_preview(assistant_text)
    threads.update_metadata(thread_id, title, preview)


def persist_assistant_only(
    db: Connection,
    thread_id: str,
    assistant_text: str,
) -> None:
    messages = ThreadMessageRepository(db)
    threads = ThreadRepository(db)
    messages.append(thread_id, "assistant", assistant_text)
    preview = _trim_preview(assistant_text)
    threads.update_preview(thread_id, preview)
