"""Tests for the chat-persistence service against the test database."""
from app.repositories.user_repository import UserRepository
from app.repositories.thread_repository import ThreadRepository
from app.repositories.thread_message_repository import ThreadMessageRepository
from app.services import chat_persistence as cp


def _make_thread(conn):
    owner = UserRepository(conn).mirror_user_from_redmine(123, "u@example.com", "User", "member")["id"]
    return ThreadRepository(conn).create_thread(owner)


def test_persist_user_and_assistant_appends_both(test_db_connection):
    thread_id = _make_thread(test_db_connection)
    cp.persist_user_and_assistant(test_db_connection, thread_id, "Create a new task", "Created it.")

    messages = ThreadMessageRepository(test_db_connection).list_for_thread(thread_id)
    assert [m["role"] for m in messages] == ["user", "assistant"]
    assert messages[0]["content"] == "Create a new task"
    assert messages[1]["content"] == "Created it."


def test_persist_assistant_only_appends_one(test_db_connection):
    thread_id = _make_thread(test_db_connection)
    cp.persist_assistant_only(test_db_connection, thread_id, "assistant reply")

    messages = ThreadMessageRepository(test_db_connection).list_for_thread(thread_id)
    assert len(messages) == 1
    assert messages[0]["role"] == "assistant"
    assert messages[0]["content"] == "assistant reply"
