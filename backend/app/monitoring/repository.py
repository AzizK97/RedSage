from datetime import datetime, timezone
from typing import Any

from psycopg import Connection


class MonitoringRepository:
    def __init__(self, db: Connection) -> None:
        self.db = db

    def ensure_tables(self) -> None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS monitoring_runs (
                    id TEXT PRIMARY KEY,
                    started_at TIMESTAMPTZ NOT NULL,
                    finished_at TIMESTAMPTZ,
                    status TEXT NOT NULL,
                    error_text TEXT,
                    projects_count INTEGER DEFAULT 0,
                    issues_count INTEGER DEFAULT 0,
                    events_count INTEGER DEFAULT 0,
                    synced_pms INTEGER DEFAULT 0
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS monitoring_project_snapshots (
                    run_id TEXT NOT NULL REFERENCES monitoring_runs(id) ON DELETE CASCADE,
                    project_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    open_issues INTEGER NOT NULL,
                    in_progress_issues INTEGER NOT NULL,
                    overdue_issues INTEGER NOT NULL,
                    critical_open_issues INTEGER NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL,
                    PRIMARY KEY (run_id, project_id)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS monitoring_issue_snapshots (
                    run_id TEXT NOT NULL REFERENCES monitoring_runs(id) ON DELETE CASCADE,
                    issue_id INTEGER NOT NULL,
                    project_id INTEGER,
                    subject TEXT,
                    status TEXT,
                    priority TEXT,
                    due_date DATE,
                    updated_on TIMESTAMPTZ,
                    PRIMARY KEY (run_id, issue_id)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS monitoring_events (
                    id BIGSERIAL PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES monitoring_runs(id) ON DELETE CASCADE,
                    project_id INTEGER,
                    issue_id INTEGER,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    details TEXT,
                    fingerprint TEXT NOT NULL,
                    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE(fingerprint)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS monitoring_notifications (
                    id BIGSERIAL PRIMARY KEY,
                    event_id BIGINT NOT NULL REFERENCES monitoring_events(id) ON DELETE CASCADE,
                    channel TEXT NOT NULL,
                    status TEXT NOT NULL,
                    response_text TEXT,
                    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        self.db.commit()

    def start_run(self, run_id: str) -> None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO monitoring_runs (id, started_at, status)
                VALUES (%s, %s, 'running')
                """,
                (run_id, datetime.now(timezone.utc)),
            )
        self.db.commit()

    def finish_run(
        self,
        run_id: str,
        *,
        status: str,
        projects_count: int,
        issues_count: int,
        events_count: int,
        synced_pms: int,
        error_text: str | None = None,
    ) -> None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                UPDATE monitoring_runs
                SET finished_at = %s,
                    status = %s,
                    error_text = %s,
                    projects_count = %s,
                    issues_count = %s,
                    events_count = %s,
                    synced_pms = %s
                WHERE id = %s
                """,
                (
                    datetime.now(timezone.utc),
                    status,
                    error_text,
                    projects_count,
                    issues_count,
                    events_count,
                    synced_pms,
                    run_id,
                ),
            )
        self.db.commit()

    def save_project_snapshots(self, run_id: str, snapshots: list[dict[str, Any]]) -> None:
        if not snapshots:
            return
        with self.db.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO monitoring_project_snapshots (
                    run_id, project_id, project_name, open_issues, in_progress_issues,
                    overdue_issues, critical_open_issues, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    (
                        run_id,
                        row["project_id"],
                        row["project_name"],
                        row["open_issues"],
                        row["in_progress_issues"],
                        row["overdue_issues"],
                        row["critical_open_issues"],
                        datetime.now(timezone.utc),
                    )
                    for row in snapshots
                ],
            )
        self.db.commit()

    def save_issue_snapshots(self, run_id: str, issues: list[dict[str, Any]]) -> None:
        if not issues:
            return
        with self.db.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO monitoring_issue_snapshots (
                    run_id, issue_id, project_id, subject, status, priority, due_date, updated_on
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    (
                        run_id,
                        row.get("issue_id"),
                        row.get("project_id"),
                        row.get("subject"),
                        row.get("status"),
                        row.get("priority"),
                        row.get("due_date"),
                        row.get("updated_on"),
                    )
                    for row in issues
                ],
            )
        self.db.commit()

    def save_events(self, run_id: str, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        stored: list[dict[str, Any]] = []
        if not events:
            return stored

        with self.db.cursor() as cur:
            for event in events:
                cur.execute(
                    """
                    INSERT INTO monitoring_events (
                        run_id, project_id, issue_id, event_type, severity, title, details, fingerprint
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (fingerprint) DO NOTHING
                    RETURNING id
                    """,
                    (
                        run_id,
                        event.get("project_id"),
                        event.get("issue_id"),
                        event["event_type"],
                        event["severity"],
                        event["title"],
                        event.get("details", ""),
                        event["fingerprint"],
                    ),
                )
                row = cur.fetchone()
                if row:
                    stored.append({**event, "id": row[0]})
        self.db.commit()
        return stored

    def record_notification(
        self,
        *,
        event_id: int,
        channel: str,
        status: str,
        response_text: str = "",
    ) -> None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO monitoring_notifications (event_id, channel, status, response_text)
                VALUES (%s, %s, %s, %s)
                """,
                (event_id, channel, status, response_text),
            )
        self.db.commit()

    def get_latest_project_snapshots(self) -> dict[int, dict[str, Any]]:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT s.project_id,
                       s.project_name,
                       s.open_issues,
                       s.in_progress_issues,
                       s.overdue_issues,
                       s.critical_open_issues
                FROM monitoring_project_snapshots s
                JOIN monitoring_runs r ON r.id = s.run_id
                WHERE r.status = 'success'
                  AND r.started_at = (
                      SELECT MAX(started_at) FROM monitoring_runs WHERE status = 'success'
                  )
                """
            )
            rows = cur.fetchall()
        return {
            row[0]: {
                "project_id": row[0],
                "project_name": row[1],
                "open_issues": row[2],
                "in_progress_issues": row[3],
                "overdue_issues": row[4],
                "critical_open_issues": row[5],
            }
            for row in rows
        }

    def get_latest_issue_states(self) -> dict[int, dict[str, Any]]:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT i.issue_id, i.project_id, i.subject, i.status, i.priority, i.due_date, i.updated_on
                FROM monitoring_issue_snapshots i
                JOIN monitoring_runs r ON r.id = i.run_id
                WHERE r.status = 'success'
                  AND r.started_at = (
                      SELECT MAX(started_at) FROM monitoring_runs WHERE status = 'success'
                  )
                """
            )
            rows = cur.fetchall()

        return {
            row[0]: {
                "issue_id": row[0],
                "project_id": row[1],
                "subject": row[2],
                "status": row[3],
                "priority": row[4],
                "due_date": row[5],
                "updated_on": row[6],
            }
            for row in rows
        }

    def get_recent_notifications(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT id, event_type, severity, title, details, occurred_at, project_id, issue_id
                FROM monitoring_events
                ORDER BY occurred_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
        return [
            {
                "id": row[0],
                "event_type": row[1],
                "severity": row[2],
                "title": row[3],
                "details": row[4],
                "occurred_at": row[5],
                "project_id": row[6],
                "issue_id": row[7],
            }
            for row in rows
        ]

    def get_overview(self) -> dict[str, Any]:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT id, started_at, projects_count, issues_count, events_count, synced_pms
                FROM monitoring_runs
                WHERE status = 'success'
                ORDER BY started_at DESC
                LIMIT 1
                """
            )
            last_run = cur.fetchone()

            if not last_run:
                return {
                    "metrics": {
                        "total_projects": 0,
                        "open_issues": 0,
                        "in_progress": 0,
                        "overdue": 0,
                        "critical": 0,
                    },
                    "last_run": None,
                    "project_status": [],
                    "run_trend": [],
                    "recent_events": [],
                }

            run_id = last_run[0]
            cur.execute(
                """
                SELECT
                  COALESCE(SUM(open_issues), 0),
                  COALESCE(SUM(in_progress_issues), 0),
                  COALESCE(SUM(overdue_issues), 0),
                  COALESCE(SUM(critical_open_issues), 0),
                  COUNT(*)
                FROM monitoring_project_snapshots
                WHERE run_id = %s
                """,
                (run_id,),
            )
            summary = cur.fetchone()

            cur.execute(
                """
                SELECT event_type, severity, title, details, occurred_at, project_id, issue_id
                FROM monitoring_events
                ORDER BY occurred_at DESC
                LIMIT 20
                """
            )
            events_rows = cur.fetchall()

            cur.execute(
                """
                SELECT project_id, project_name, open_issues, in_progress_issues, overdue_issues, critical_open_issues
                FROM monitoring_project_snapshots
                WHERE run_id = %s
                ORDER BY overdue_issues DESC, critical_open_issues DESC, open_issues DESC
                LIMIT 12
                """,
                (run_id,),
            )
            project_rows = cur.fetchall()

            cur.execute(
                """
                SELECT started_at, events_count
                FROM monitoring_runs
                WHERE status = 'success'
                ORDER BY started_at DESC
                LIMIT 8
                """
            )
            trend_rows = cur.fetchall()

        return {
            "metrics": {
                "total_projects": int(summary[4] or 0),
                "open_issues": int(summary[0] or 0),
                "in_progress": int(summary[1] or 0),
                "overdue": int(summary[2] or 0),
                "critical": int(summary[3] or 0),
            },
            "last_run": {
                "id": last_run[0],
                "started_at": last_run[1],
                "projects_count": int(last_run[2] or 0),
                "issues_count": int(last_run[3] or 0),
                "events_count": int(last_run[4] or 0),
                "synced_pms": int(last_run[5] or 0),
            },
            "project_status": [
                {
                    "project_id": row[0],
                    "project_name": row[1],
                    "open_issues": int(row[2] or 0),
                    "in_progress": int(row[3] or 0),
                    "overdue": int(row[4] or 0),
                    "critical": int(row[5] or 0),
                }
                for row in project_rows
            ],
            "run_trend": [
                {
                    "started_at": row[0],
                    "events_count": int(row[1] or 0),
                }
                for row in reversed(trend_rows)
            ],
            "recent_events": [
                {
                    "event_type": row[0],
                    "severity": row[1],
                    "title": row[2],
                    "details": row[3],
                    "occurred_at": row[4],
                    "project_id": row[5],
                    "issue_id": row[6],
                }
                for row in events_rows
            ],
        }
