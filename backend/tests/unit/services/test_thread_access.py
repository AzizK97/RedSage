"""Tests for the thread-access (ownership) service against the test database."""
import pytest
from fastapi import HTTPException

from app.repositories.user_repository import UserRepository
from app.repositories.thread_repository import ThreadRepository
from app.services.thread_access import ensure_thread_owner


def _make_user(conn, redmine_user_id):
    return UserRepository(conn).mirror_user_from_redmine(
        redmine_user_id, f"u{redmine_user_id}@example.com", "User", "member"
    )["id"]


def test_binds_owner_when_thread_is_new(test_db_connection):
    user = _make_user(test_db_connection, 123)
    ensure_thread_owner(test_db_connection, "thread-1", user)
    assert ThreadRepository(test_db_connection).get_owner("thread-1") == user


def test_same_owner_is_allowed(test_db_connection):
    user = _make_user(test_db_connection, 123)
    ensure_thread_owner(test_db_connection, "thread-1", user)
    # A second call by the same owner must not raise.
    ensure_thread_owner(test_db_connection, "thread-1", user)


def test_foreign_owner_is_forbidden(test_db_connection):
    owner = _make_user(test_db_connection, 123)
    intruder = _make_user(test_db_connection, 124)
    ensure_thread_owner(test_db_connection, "thread-1", owner)

    with pytest.raises(HTTPException) as exc:
        ensure_thread_owner(test_db_connection, "thread-1", intruder)
    assert exc.value.status_code == 403


def test_blank_thread_id_is_rejected(test_db_connection):
    user = _make_user(test_db_connection, 123)
    with pytest.raises(HTTPException) as exc:
        ensure_thread_owner(test_db_connection, "   ", user)
    assert exc.value.status_code == 400
