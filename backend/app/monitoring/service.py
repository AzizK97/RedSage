import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any

import psycopg
import requests

from app.core.config import settings
from app.integrations.redmine_client import redmine_client
from app.monitoring.cache import MonitoringCache
from app.monitoring.repository import MonitoringRepository
from app.services.user_sync_service import UserSyncService


@dataclass
class MonitoringEvent:
    event_type: str
    severity: str
    title: str
    details: str
    fingerprint: str
    project_id: int | None = None
    issue_id: int | None = None


class MonitoringService:
    def __init__(self, cache: MonitoringCache | None = None) -> None:
        self.cache = cache or MonitoringCache()
        self.lock_key = "monitoring:run:lock"
        self.cache_key_overview = "monitoring:overview"

    async def close(self) -> None:
        await self.cache.close()

    def _issue_closed(self, issue: dict[str, Any]) -> bool:
        status_name = ((issue.get("status") or {}).get("name") or "").lower()
        return "closed" in status_name or "resolved" in status_name

    def _issue_in_progress(self, issue: dict[str, Any]) -> bool:
        status_name = ((issue.get("status") or {}).get("name") or "").lower()
        return "progress" in status_name

    def _issue_critical(self, issue: dict[str, Any]) -> bool:
        priority = ((issue.get("priority") or {}).get("name") or "").lower()
        return any(tag in priority for tag in ["high", "urgent", "immediate", "critical"])

    def _issue_due_date(self, issue: dict[str, Any]) -> date | None:
        raw_due = issue.get("due_date")
        if not raw_due:
            return None
        try:
            return date.fromisoformat(str(raw_due))
        except Exception:
            return None

    def _project_snapshots(self, projects: list[dict[str, Any]], issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
        now_date = date.today()
        by_project: dict[int, dict[str, Any]] = {
            int(project["id"]): {
                "project_id": int(project["id"]),
                "project_name": project.get("name", f"Project {project['id']}"),
                "open_issues": 0,
                "in_progress_issues": 0,
                "overdue_issues": 0,
                "critical_open_issues": 0,
            }
            for project in projects
        }

        for issue in issues:
            project = issue.get("project") or {}
            project_id = int(project.get("id", 0))
            if project_id <= 0 or project_id not in by_project:
                continue

            is_closed = self._issue_closed(issue)
            due_date = self._issue_due_date(issue)

            if not is_closed:
                by_project[project_id]["open_issues"] += 1

                if self._issue_in_progress(issue):
                    by_project[project_id]["in_progress_issues"] += 1

                if due_date and due_date < now_date:
                    by_project[project_id]["overdue_issues"] += 1

                if self._issue_critical(issue):
                    by_project[project_id]["critical_open_issues"] += 1

        return list(by_project.values())

    def _issue_states(self, issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
        states: list[dict[str, Any]] = []
        for issue in issues:
            issue_id = int(issue.get("id", 0))
            if issue_id <= 0:
                continue
            project = issue.get("project") or {}
            states.append(
                {
                    "issue_id": issue_id,
                    "project_id": int(project.get("id", 0)) or None,
                    "subject": issue.get("subject") or "",
                    "status": ((issue.get("status") or {}).get("name") or ""),
                    "priority": ((issue.get("priority") or {}).get("name") or ""),
                    "due_date": self._issue_due_date(issue),
                    "updated_on": redmine_client.parse_redmine_datetime(issue.get("updated_on")),
                }
            )
        return states

    def _build_events(
        self,
        *,
        prev_projects: dict[int, dict[str, Any]],
        new_projects: list[dict[str, Any]],
        prev_issues: dict[int, dict[str, Any]],
        new_issue_states: list[dict[str, Any]],
    ) -> list[MonitoringEvent]:
        events: list[MonitoringEvent] = []
        now_token = datetime.now(timezone.utc).strftime("%Y%m%d%H")

        new_project_map = {row["project_id"]: row for row in new_projects}

        for project_id, snapshot in new_project_map.items():
            previous = prev_projects.get(project_id)
            if previous is None:
                events.append(
                    MonitoringEvent(
                        event_type="project_detected",
                        severity="info",
                        title=f"New tracked project: {snapshot['project_name']}",
                        details="Project appeared in Redmine monitoring snapshot.",
                        fingerprint=f"project_detected:{project_id}:{now_token}",
                        project_id=project_id,
                    )
                )
                continue

            if snapshot["overdue_issues"] > previous.get("overdue_issues", 0):
                delta = snapshot["overdue_issues"] - previous.get("overdue_issues", 0)
                events.append(
                    MonitoringEvent(
                        event_type="overdue_increase",
                        severity="important",
                        title=f"Overdue tasks increased in {snapshot['project_name']}",
                        details=f"{delta} additional overdue task(s) detected.",
                        fingerprint=f"overdue:{project_id}:{snapshot['overdue_issues']}",
                        project_id=project_id,
                    )
                )

            if snapshot["critical_open_issues"] > previous.get("critical_open_issues", 0):
                delta = snapshot["critical_open_issues"] - previous.get("critical_open_issues", 0)
                events.append(
                    MonitoringEvent(
                        event_type="critical_issue_increase",
                        severity="critical",
                        title=f"Critical issues increased in {snapshot['project_name']}",
                        details=f"{delta} critical task(s) added or escalated.",
                        fingerprint=f"critical:{project_id}:{snapshot['critical_open_issues']}",
                        project_id=project_id,
                    )
                )

        due_soon_limit = date.today() + timedelta(hours=settings.MONITORING_DUE_SOON_HOURS)
        next_issue_state = {row["issue_id"]: row for row in new_issue_states}
        for issue_id, state in next_issue_state.items():
            previous = prev_issues.get(issue_id)
            subject = state.get("subject") or f"Issue #{issue_id}"

            if previous is None:
                events.append(
                    MonitoringEvent(
                        event_type="issue_created",
                        severity="info",
                        title=f"New task created: {subject}",
                        details=f"Status: {state.get('status') or 'unknown'}.",
                        fingerprint=f"issue_created:{issue_id}:{now_token}",
                        project_id=state.get("project_id"),
                        issue_id=issue_id,
                    )
                )
            else:
                prev_status = (previous.get("status") or "").strip()
                status = (state.get("status") or "").strip()
                if prev_status != status:
                    severity = "important" if "progress" in status.lower() else "info"
                    events.append(
                        MonitoringEvent(
                            event_type="issue_status_changed",
                            severity=severity,
                            title=f"Task status changed: {subject}",
                            details=f"{prev_status or 'Unknown'} → {status or 'Unknown'}",
                            fingerprint=f"status:{issue_id}:{status}",
                            project_id=state.get("project_id"),
                            issue_id=issue_id,
                        )
                    )

            due_date = state.get("due_date")
            if isinstance(due_date, date) and due_date <= due_soon_limit and not (state.get("status") or "").lower().startswith("closed"):
                events.append(
                    MonitoringEvent(
                        event_type="issue_due_soon",
                        severity="important",
                        title=f"Task due soon: {subject}",
                        details=f"Due date: {due_date.isoformat()}",
                        fingerprint=f"due_soon:{issue_id}:{due_date.isoformat()}",
                        project_id=state.get("project_id"),
                        issue_id=issue_id,
                    )
                )

        return events

    async def _send_slack(self, event: dict[str, Any], repo: MonitoringRepository) -> None:
        if not settings.SLACK_WEBHOOK_URL:
            return

        if event["severity"] not in {"critical", "important"}:
            return

        dedupe_key = f"monitoring:slack:{event['fingerprint']}"
        is_new = await self.cache.set_if_absent(
            dedupe_key,
            "1",
            settings.MONITORING_ALERT_COOLDOWN_SECONDS,
        )
        if not is_new:
            repo.record_notification(
                event_id=event["id"],
                channel="slack",
                status="skipped_cooldown",
                response_text="Deduplicated by Redis cooldown",
            )
            return

        payload = {
            "text": f"[{event['severity'].upper()}] {event['title']}\n{event.get('details', '')}".strip(),
        }

        try:
            response = requests.post(
                settings.SLACK_WEBHOOK_URL,
                json=payload,
                timeout=8,
            )
            if response.status_code >= 300:
                repo.record_notification(
                    event_id=event["id"],
                    channel="slack",
                    status="failed",
                    response_text=f"{response.status_code}: {response.text}",
                )
            else:
                repo.record_notification(
                    event_id=event["id"],
                    channel="slack",
                    status="sent",
                    response_text="ok",
                )
        except Exception as exc:
            repo.record_notification(
                event_id=event["id"],
                channel="slack",
                status="failed",
                response_text=str(exc),
            )

    async def run_once(self) -> dict[str, Any]:
        if not settings.PLATFORM_POSTGRES_URL:
            raise RuntimeError("PLATFORM_POSTGRES_URL is not configured")

        acquired = await self.cache.acquire_lock(
            self.lock_key,
            ttl_seconds=max(30, settings.MONITORING_INTERVAL_SECONDS),
        )
        if not acquired:
            return {"status": "skipped", "reason": "monitoring job already running"}

        run_id = str(uuid.uuid4())
        synced_count = 0
        events_count = 0
        projects_count = 0
        issues_count = 0

        db = psycopg.connect(settings.PLATFORM_POSTGRES_URL)
        try:
            repo = MonitoringRepository(db)
            repo.ensure_tables()
            repo.start_run(run_id)

            prev_projects = repo.get_latest_project_snapshots()
            prev_issues = repo.get_latest_issue_states()

            projects = redmine_client.list_projects()
            issues = redmine_client.list_issues()

            projects_count = len(projects)
            issues_count = len(issues)

            project_snapshots = self._project_snapshots(projects, issues)
            issue_states = self._issue_states(issues)
            generated_events = self._build_events(
                prev_projects=prev_projects,
                new_projects=project_snapshots,
                prev_issues=prev_issues,
                new_issue_states=issue_states,
            )

            repo.save_project_snapshots(run_id, project_snapshots)
            repo.save_issue_snapshots(run_id, issue_states)
            stored_events = repo.save_events(
                run_id,
                [event.__dict__ for event in generated_events],
            )
            events_count = len(stored_events)

            for event in stored_events:
                repo.record_notification(
                    event_id=event["id"],
                    channel="in_app",
                    status="queued",
                    response_text="stored",
                )
                await self._send_slack(event, repo)

            synced_count = UserSyncService(db).sync_project_managers()

            repo.finish_run(
                run_id,
                status="success",
                projects_count=projects_count,
                issues_count=issues_count,
                events_count=events_count,
                synced_pms=synced_count,
            )

            await self.cache.delete(self.cache_key_overview)

            return {
                "status": "success",
                "run_id": run_id,
                "projects_count": projects_count,
                "issues_count": issues_count,
                "events_count": events_count,
                "synced_pms": synced_count,
            }
        except Exception as exc:
            try:
                repo = MonitoringRepository(db)
                repo.ensure_tables()
                repo.finish_run(
                    run_id,
                    status="failed",
                    projects_count=projects_count,
                    issues_count=issues_count,
                    events_count=events_count,
                    synced_pms=synced_count,
                    error_text=str(exc),
                )
            except Exception:
                pass
            raise
        finally:
            db.close()
            await self.cache.release_lock(self.lock_key)

    async def get_overview(self) -> dict[str, Any]:
        cached = await self.cache.get_json(self.cache_key_overview)
        if cached is not None:
            return cached

        if not settings.PLATFORM_POSTGRES_URL:
            raise RuntimeError("PLATFORM_POSTGRES_URL is not configured")

        db = psycopg.connect(settings.PLATFORM_POSTGRES_URL)
        try:
            repo = MonitoringRepository(db)
            repo.ensure_tables()
            data = repo.get_overview()
            await self.cache.set_json(
                self.cache_key_overview,
                data,
                ttl_seconds=settings.MONITORING_CACHE_TTL_SECONDS,
            )
            return data
        finally:
            db.close()
