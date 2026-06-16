"""Unit tests for the monitoring event-derivation logic.

``MonitoringService._build_events`` is the heart of the proactive monitoring
pipeline: it emits events by diffing the current snapshot against the previous
run, never from absolute values. These tests exercise that logic in isolation,
with no database or Redis.
"""
from datetime import date, timedelta

from app.services.monitoring_service import MonitoringService as ServiceFacade  # noqa: F401
from app.monitoring.service import MonitoringService


def _svc():
    # Pass a dummy cache so __init__ does not construct a real Redis client;
    # _build_events does not touch the cache.
    return MonitoringService(cache=object())


def _types(events):
    return {(e.event_type, e.severity) for e in events}


def test_new_project_emits_project_detected():
    events = _svc()._build_events(
        prev_projects={},
        new_projects=[{
            "project_id": 1, "project_name": "Alpha",
            "open_issues": 0, "in_progress_issues": 0,
            "overdue_issues": 0, "critical_open_issues": 0,
        }],
        prev_issues={},
        new_issue_states=[],
    )
    assert ("project_detected", "info") in _types(events)


def test_overdue_and_critical_increases():
    prev = {1: {"overdue_issues": 0, "critical_open_issues": 0}}
    new = [{
        "project_id": 1, "project_name": "Alpha",
        "open_issues": 5, "in_progress_issues": 1,
        "overdue_issues": 2, "critical_open_issues": 1,
    }]
    types = _types(_svc()._build_events(
        prev_projects=prev, new_projects=new, prev_issues={}, new_issue_states=[],
    ))
    assert ("overdue_increase", "important") in types
    assert ("critical_issue_increase", "critical") in types


def test_new_issue_emits_issue_created():
    events = _svc()._build_events(
        prev_projects={}, new_projects=[], prev_issues={},
        new_issue_states=[{
            "issue_id": 101, "project_id": 1, "subject": "New task",
            "status": "New", "priority": "Normal", "due_date": None,
        }],
    )
    assert ("issue_created", "info") in _types(events)


def test_status_change_to_in_progress_is_important():
    prev = {101: {"status": "New"}}
    new = [{
        "issue_id": 101, "project_id": 1, "subject": "Task",
        "status": "In Progress", "priority": "Normal", "due_date": None,
    }]
    types = _types(_svc()._build_events(
        prev_projects={}, new_projects=[], prev_issues=prev, new_issue_states=new,
    ))
    assert ("issue_status_changed", "important") in types


def test_issue_due_soon_is_flagged():
    prev = {101: {"status": "New"}}
    new = [{
        "issue_id": 101, "project_id": 1, "subject": "Task",
        "status": "New", "priority": "Normal", "due_date": date.today(),
    }]
    types = _types(_svc()._build_events(
        prev_projects={}, new_projects=[], prev_issues=prev, new_issue_states=new,
    ))
    assert ("issue_due_soon", "important") in types


def test_stable_snapshot_emits_no_events():
    prev_projects = {1: {"overdue_issues": 2, "critical_open_issues": 1}}
    new_projects = [{
        "project_id": 1, "project_name": "Alpha",
        "open_issues": 5, "in_progress_issues": 1,
        "overdue_issues": 2, "critical_open_issues": 1,
    }]
    prev_issues = {101: {"status": "New"}}
    new_issue_states = [{
        "issue_id": 101, "project_id": 1, "subject": "Task",
        "status": "New", "priority": "Normal",
        "due_date": date.today() + timedelta(days=3650),
    }]
    events = _svc()._build_events(
        prev_projects=prev_projects, new_projects=new_projects,
        prev_issues=prev_issues, new_issue_states=new_issue_states,
    )
    assert events == []
