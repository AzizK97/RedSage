"""Unit tests for role-based access control enforced at the read-tool boundary.

These verify that ``set_session_user`` correctly computes the set of projects a
project manager may see, and that the read tools honour that scope. They run
fully offline: the Redmine client and the cache are replaced with fakes.
"""
import pytest

from app.agent.tools import read


# Two projects exist in Redmine; the project manager (id 19) holds a
# "Manager" role only in "alpha", and a plain "Developer" role in "beta".
_PROJECTS = {"projects": [
    {"id": 1, "name": "Alpha", "identifier": "alpha", "description": ""},
    {"id": 2, "name": "Beta", "identifier": "beta", "description": ""},
]}

_MEMBERSHIPS = {
    "alpha": {"memberships": [
        {"user": {"id": 19}, "roles": [{"name": "Manager"}]},
    ]},
    "beta": {"memberships": [
        {"user": {"id": 19}, "roles": [{"name": "Developer"}]},
    ]},
}

_ONE_ISSUE = {"total_count": 1, "issues": [
    {"id": 1, "subject": "T", "status": {"name": "New"},
     "priority": {"name": "Normal"}, "project": {"name": "Alpha"}},
]}


def _fake_get(path, params=None):
    if path == "/projects.json":
        return _PROJECTS
    if path.endswith("/memberships.json"):
        identifier = path.split("/")[2]
        return _MEMBERSHIPS.get(identifier, {"memberships": []})
    if path == "/issues.json":
        return _ONE_ISSUE
    return {}


@pytest.fixture(autouse=True)
def _isolate_session(monkeypatch):
    """Force the cache to miss and stub the Redmine client for every test."""
    monkeypatch.setattr(read, "get_cached_sync", lambda *a, **k: None)
    monkeypatch.setattr(read, "set_cached_sync", lambda *a, **k: None)
    monkeypatch.setattr(read.redmine_client, "get", _fake_get)
    yield
    read.clear_session_user()


def test_admin_has_no_project_restriction():
    read.set_session_user(1, is_admin=True)
    assert read._ALLOWED_PROJECT_IDENTIFIERS is None

    projects = read.get_projects.invoke({})
    assert {p["identifier"] for p in projects["projects"]} == {"alpha", "beta"}


def test_project_manager_is_scoped_to_managed_projects():
    read.set_session_user(19, is_admin=False)
    # Only the project where the user holds a managerial role.
    assert read._ALLOWED_PROJECT_IDENTIFIERS == {"alpha"}

    projects = read.get_projects.invoke({})
    assert {p["identifier"] for p in projects["projects"]} == {"alpha"}


def test_get_issues_blocks_a_disallowed_project():
    read.set_session_user(19, is_admin=False)

    # The managed project is allowed through to the API and returns data.
    allowed = read.get_issues.invoke({"project_id": "alpha"})
    assert allowed["total_count"] == 1

    # A project the user does not manage is refused without hitting Redmine.
    blocked = read.get_issues.invoke({"project_id": "beta"})
    assert blocked == {"total_count": 0, "issues": []}


def test_scope_fails_closed_when_redmine_is_unreachable(monkeypatch):
    def _boom(path, params=None):
        raise RuntimeError("redmine down")

    # Scope computation fails -> deny access (empty allow-set), not widen it.
    monkeypatch.setattr(read.redmine_client, "get", _boom)
    read.set_session_user(19, is_admin=False)
    assert read._ALLOWED_PROJECT_IDENTIFIERS == set()

    # With an empty allow-set, the read tools return nothing.
    monkeypatch.setattr(read.redmine_client, "get", _fake_get)
    projects = read.get_projects.invoke({})
    assert projects["projects"] == []
