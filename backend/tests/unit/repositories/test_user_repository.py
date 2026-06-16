"""Tests for UserRepository against the test database."""
from app.repositories.user_repository import UserRepository


def test_insert_and_fetch_user(test_db_connection):
    repo = UserRepository(test_db_connection)
    created = repo.mirror_user_from_redmine(123, "admin@example.com", "Admin User", "admin")

    assert created["platform_role"] == "admin"
    fetched = repo.get_by_redmine_user_id(123)
    assert fetched["email"] == "admin@example.com"
    assert fetched["full_name"] == "Admin User"


def test_new_user_defaults_to_member(test_db_connection):
    repo = UserRepository(test_db_connection)
    created = repo.mirror_user_from_redmine(200, "m@example.com", "Member", None)
    assert created["platform_role"] == "member"


def test_update_never_demotes_an_admin(test_db_connection):
    repo = UserRepository(test_db_connection)
    repo.mirror_user_from_redmine(123, "admin@example.com", "Admin User", "admin")

    # An ordinary login (platform_role=None) must update the profile but keep admin.
    updated = repo.mirror_user_from_redmine(123, "new@example.com", "Admin User", None)
    assert updated["platform_role"] == "admin"
    assert updated["email"] == "new@example.com"


def test_list_by_role(test_db_connection):
    repo = UserRepository(test_db_connection)
    repo.mirror_user_from_redmine(123, "admin@example.com", "Admin User", "admin")
    repo.mirror_user_from_redmine(200, "member@example.com", "Member", "member")

    admins = repo.list_by_role("admin")
    assert [a["redmine_user_id"] for a in admins] == [123]
