from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, TypedDict

import requests
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from app.agent.agents.notification_summary import create_notification_summary_agent
from app.agent.supervisor import create_llm
from app.core.settings import settings
from app.integrations.redmine_client import redmine_client

"""
DEPRECATED — LangGraph monitoring prototype (not used in production).

This module was an earlier proof-of-concept that ran the monitoring pipeline
as a LangGraph StateGraph. It has been superseded by MonitoringService in
app/monitoring/service.py, which is the active implementation called by the
scheduler and the /api/monitoring endpoints.

Kept for reference only. Do not wire this into any router or scheduler job.
"""


class MonitoringState(TypedDict):
    events: list[dict[str, Any]]
    summary: str
    notification: dict[str, Any]
    slack_message: str
    slack_sent: bool
    error: str
    as_of: str


def _fetch_recent_project_events() -> list[dict[str, Any]]:
    projects = redmine_client.list_projects()
    if not projects:
        return []

    lookback = max(10, settings.MONITORING_LOOKBACK_MINUTES)
    since = datetime.now(timezone.utc) - timedelta(minutes=lookback)
    updated_since = since.strftime("%Y-%m-%dT%H:%M:%SZ")

    events: list[dict[str, Any]] = []
    for project in projects:
        identifier = (project.get("identifier") or "").strip()
        if not identifier:
            continue

        url = f"{redmine_client.base_url}/issues.json"
        resp = requests.get(
            url,
            headers=redmine_client.headers,
            params={
                "project_id": identifier,
                "status_id": "*",
                "updated_on": f">={updated_since}",
                "limit": 100,
                "offset": 0,
            },
            timeout=20,
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"REDMINE_API_ERROR: {resp.status_code} - {resp.text}")

        issues = resp.json().get("issues", [])
        if not issues:
            continue

        overdue = 0
        closed = 0
        overdue_items: list[dict[str, Any]] = []
        closed_items: list[dict[str, Any]] = []
        for issue in issues:
            issue_id = issue.get("id")
            subject = (issue.get("subject") or "").strip()
            status_name = str((issue.get("status") or {}).get("name", "")).lower()
            if "closed" in status_name or "resolved" in status_name:
                closed += 1
                if len(closed_items) < 3:
                    closed_items.append(
                        {
                            "id": issue_id,
                            "subject": subject,
                            "status": issue.get("status", {}).get("name", ""),
                        }
                    )

            due_date = issue.get("due_date")
            if due_date and due_date < datetime.now().date().isoformat() and "closed" not in status_name:
                overdue += 1
                if len(overdue_items) < 3:
                    overdue_items.append(
                        {
                            "id": issue_id,
                            "subject": subject,
                            "due_date": due_date,
                            "status": issue.get("status", {}).get("name", ""),
                        }
                    )

        events.append(
            {
                "project_id": project.get("id"),
                "project_name": project.get("name"),
                "project_identifier": identifier,
                "updated_issues": len(issues),
                "closed_issues": closed,
                "overdue_issues": overdue,
                "overdue_items": overdue_items,
                "closed_items": closed_items,
                "project_url": f"{redmine_client.base_url}/projects/{identifier}",
            }
        )
    return events


def _collect_events(state: MonitoringState) -> MonitoringState:
    try:
        events = _fetch_recent_project_events()
        return {**state, "events": events, "error": ""}
    except Exception as exc:
        return {**state, "events": [], "error": str(exc)}


def _summarize_events(state: MonitoringState) -> MonitoringState:
    if state.get("error"):
        return {**state, "summary": f"Monitoring failed during data collection: {state['error']}"}
    events = state.get("events", [])
    if not events:
        return {**state, "summary": "No meaningful Redmine changes were detected in the latest monitoring window."}

    llm = create_llm()
    summary_agent = create_notification_summary_agent(llm)
    prompt = (
        "Summarize these Redmine monitoring events for Slack notification. "
        "Use simple professional wording. Include momentum, risk, overdue status, and one action item. "
        "Mention specific project names and ticket IDs when available.\n\n"
        f"Events: {events}"
    )
    result = summary_agent.invoke({"messages": [HumanMessage(content=prompt)]})
    messages = result.get("messages", []) if isinstance(result, dict) else getattr(result, "messages", [])
    summary_text = str(messages[-1].content).strip() if messages else "Monitoring summary unavailable."
    return {**state, "summary": summary_text}


def _format_notification_payload(state: MonitoringState) -> MonitoringState:
    events = state.get("events", [])
    summary = state.get("summary", "").strip()
    as_of = state.get("as_of", "")

    total_closed = sum(int(item.get("closed_issues", 0)) for item in events)
    total_overdue = sum(int(item.get("overdue_issues", 0)) for item in events)
    at_risk = [item for item in events if int(item.get("overdue_issues", 0)) > 0]
    primary_risk = max(at_risk, key=lambda item: int(item.get("overdue_issues", 0)), default=None)

    severity = "critical" if total_overdue > 0 else ("success" if total_closed > 0 else "info")
    title = "Monitoring update"
    if total_overdue > 0:
        title = f"Overdue tasks in {(primary_risk or {}).get('project_name', 'active projects')}"
    elif total_closed > 0:
        title = "Project progress update"

    if primary_risk:
        first_overdue = (primary_risk.get("overdue_items") or [{}])[0]
        first_issue_id = first_overdue.get("id")
        first_subject = (first_overdue.get("subject") or "").strip()
        subtitle = (
            f"{primary_risk.get('project_name')}: {primary_risk.get('overdue_issues')} overdue. "
            + (f"Top risk #{first_issue_id} {first_subject}." if first_issue_id else "")
        ).strip()
        action_text = (
            f"Review overdue ticket #{first_issue_id}"
            if first_issue_id
            else f"Review overdue tasks in {primary_risk.get('project_name', 'project')}"
        )
        action_url = (
            f"{redmine_client.base_url}/issues/{first_issue_id}"
            if first_issue_id
            else str(primary_risk.get("project_url") or "/")
        )
    elif events:
        most_active = max(events, key=lambda item: int(item.get("updated_issues", 0)), default={})
        closed_examples = most_active.get("closed_items") or []
        sample = closed_examples[0] if closed_examples else {}
        sample_id = sample.get("id")
        sample_subject = (sample.get("subject") or "").strip()
        subtitle = (
            f"{most_active.get('project_name', 'Portfolio')}: {most_active.get('closed_issues', 0)} closed, no overdue. "
            + (f"Latest completion #{sample_id} {sample_subject}." if sample_id else "")
        ).strip()
        action_text = "Monitor for new blockers"
        action_url = str(most_active.get("project_url") or "/")
    else:
        subtitle = "No meaningful changes in this cycle."
        action_text = "No immediate action required"
        action_url = "/"

    notification = {
        "title": title,
        "subtitle": subtitle,
        "message": summary or subtitle,
        "severity": severity,
        "action_text": action_text,
        "action_url": action_url,
        "source": "monitoring",
        "as_of": as_of,
    }
    slack_message = "\n".join([title, summary or subtitle, f"Action: {action_text}"]).strip()
    return {**state, "notification": notification, "slack_message": slack_message}


def _send_to_slack(state: MonitoringState) -> MonitoringState:
    slack_message = state.get("slack_message", "").strip()
    if not slack_message:
        return {**state, "slack_sent": False}
    if not settings.SLACK_WEBHOOK_URL:
        return {**state, "slack_sent": False}

    resp = requests.post(
        settings.SLACK_WEBHOOK_URL,
        json={"text": slack_message},
        timeout=20,
    )
    if resp.status_code >= 400:
        return {**state, "slack_sent": False, "error": f"SLACK_SEND_FAILED: {resp.status_code} - {resp.text}"}
    return {**state, "slack_sent": True}


def _build_workflow():
    graph = StateGraph(MonitoringState)
    graph.add_node("collect_events", _collect_events)
    graph.add_node("summarize_events", _summarize_events)
    graph.add_node("format_payload", _format_notification_payload)
    graph.add_node("send_to_slack", _send_to_slack)
    graph.set_entry_point("collect_events")
    graph.add_edge("collect_events", "summarize_events")
    graph.add_edge("summarize_events", "format_payload")
    graph.add_edge("format_payload", "send_to_slack")
    graph.add_edge("send_to_slack", END)
    return graph.compile()


_monitoring_workflow = _build_workflow()


def run_monitoring_workflow() -> dict[str, Any]:
    initial_state: MonitoringState = {
        "events": [],
        "summary": "",
        "notification": {},
        "slack_message": "",
        "slack_sent": False,
        "error": "",
        "as_of": datetime.now(timezone.utc).isoformat(),
    }
    return _monitoring_workflow.invoke(initial_state)
