"""Unit tests for write-tool helpers, focused on version-id resolution.

The model frequently passes a sprint *name* or number (e.g. "0" for "sprint 0")
as ``version_id``. Sending that to Redmine raises HTTP 422 ("Target version is
not included in the list"). ``_resolve_version_id`` must map such references to a
real version id or omit them. These tests run offline with a fake Redmine client.
"""
import pytest

from app.agent.tools import write


_VERSIONS = [
    {"id": 7, "name": "Sprint 0"},
    {"id": 8, "name": "Sprint 1"},
]


@pytest.fixture(autouse=True)
def _fake_versions(monkeypatch):
    monkeypatch.setattr(
        write.redmine_client,
        "list_project_versions",
        lambda project_id: _VERSIONS,
    )


def test_resolves_sprint_name_to_real_id():
    # "0" / "sprint 0" should resolve to the "Sprint 0" version (id 7).
    assert write._resolve_version_id("talentos", "0") == "7"
    assert write._resolve_version_id("talentos", "sprint 0") == "7"


def test_keeps_a_valid_existing_id():
    assert write._resolve_version_id("talentos", "8") == "8"


def test_omits_unresolvable_reference():
    # No version named "99" / "sprint 99" exists -> omit rather than 422.
    assert write._resolve_version_id("talentos", "99") is None


def test_none_stays_none():
    assert write._resolve_version_id("talentos", None) is None


def test_falls_back_to_plausible_id_when_listing_fails(monkeypatch):
    def _boom(project_id):
        raise RuntimeError("redmine down")

    monkeypatch.setattr(write.redmine_client, "list_project_versions", _boom)
    # A positive integer is plausibly a real id and is kept; "0" is dropped.
    assert write._resolve_version_id("talentos", "8") == "8"
    assert write._resolve_version_id("talentos", "0") is None
