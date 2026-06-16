"""Tests for ThreadRepository against the test database."""
from app.repositories.user_repository import UserRepository
from app.repositories.thread_repository import ThreadRepository


def _make_owner(conn, redmine_user_id=123):
    return UserRepository(conn).mirror_user_from_redmine(
        redmine_user_id, f"u{redmine_user_id}@example.com", "User", "member"
    )["id"]


def test_create_and_list_thread(test_db_connection):
    owner = _make_owner(test_db_connection)
    repo = ThreadRepository(test_db_connection)

    thread_id = repo.create_thread(owner)
    assert repo.get_owner(thread_id) == owner
    assert any(t["thread_id"] == thread_id for t in repo.list_for_owner(owner))


def test_rename_updates_title(test_db_connection):
    owner = _make_owner(test_db_connection)
    repo = ThreadRepository(test_db_connection)
    thread_id = repo.create_thread(owner)

    repo.update_metadata(thread_id, "Renamed thread", "a preview")
    item = next(t for t in repo.list_for_owner(owner) if t["thread_id"] == thread_id)
    assert item["title"] == "Renamed thread"


def test_pending_interrupt_roundtrip(test_db_connection):
    owner = _make_owner(test_db_connection)
    repo = ThreadRepository(test_db_connection)
    thread_id = repo.create_thread(owner)

    assert repo.get_pending_interrupt(thread_id) is None
    repo.set_pending_interrupt(thread_id, {"action_requests": [{"name": "create_issue"}]})
    assert repo.get_pending_interrupt(thread_id)["action_requests"][0]["name"] == "create_issue"
    repo.clear_pending_interrupt(thread_id)
    assert repo.get_pending_interrupt(thread_id) is None


def test_delete_thread(test_db_connection):
    owner = _make_owner(test_db_connection)
    repo = ThreadRepository(test_db_connection)
    thread_id = repo.create_thread(owner)

    repo.delete_thread(thread_id)
    assert repo.get_owner(thread_id) is None
