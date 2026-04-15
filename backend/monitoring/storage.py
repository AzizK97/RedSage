import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MonitoringStorage:
    def __init__(self, db_path: str):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self) -> None:
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sync_state (
                endpoint TEXT PRIMARY KEY,
                last_sync_at TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                alert_key TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                severity TEXT NOT NULL,
                issue_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                last_sent_at TEXT,
                payload_json TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS metrics_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                project_id INTEGER,
                open_issues INTEGER NOT NULL,
                overdue_issues INTEGER NOT NULL,
                due_soon_issues INTEGER NOT NULL
            )
        """)
        self.conn.commit()

    def get_last_sync(self, endpoint: str) -> datetime | None:
        row = self.conn.execute(
            "SELECT last_sync_at FROM sync_state WHERE endpoint = ?", (endpoint,)
        ).fetchone()
        if not row:
            return None
        return datetime.fromisoformat(row["last_sync_at"])

    def set_last_sync(self, endpoint: str, dt: datetime) -> None:
        self.conn.execute("""
            INSERT INTO sync_state(endpoint, last_sync_at)
            VALUES(?, ?)
            ON CONFLICT(endpoint) DO UPDATE SET last_sync_at=excluded.last_sync_at
        """, (endpoint, dt.isoformat()))
        self.conn.commit()

    def upsert_alert(self, alert: dict, cooldown_seconds: int) -> bool:
        # Returns True if notification should be sent.
        row = self.conn.execute(
            "SELECT * FROM alerts WHERE alert_key = ?", (alert["key"],)
        ).fetchone()
        now = utcnow()

        if row is None:
            self.conn.execute("""
                INSERT INTO alerts(
                    alert_key, type, severity, issue_id, project_id, message,
                    first_seen_at, last_seen_at, last_sent_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert["key"], alert["type"], alert["severity"], alert["issue_id"],
                alert["project_id"], alert["message"], now.isoformat(), now.isoformat(),
                now.isoformat(), json.dumps(alert, default=str)
            ))
            self.conn.commit()
            return True

        last_sent = datetime.fromisoformat(row["last_sent_at"]) if row["last_sent_at"] else None
        should_notify = (
            last_sent is None or
            (now - last_sent).total_seconds() >= cooldown_seconds or
            row["severity"] != alert["severity"]
        )

        self.conn.execute("""
            UPDATE alerts
            SET severity=?, message=?, last_seen_at=?, last_sent_at=?, payload_json=?
            WHERE alert_key=?
        """, (
            alert["severity"],
            alert["message"],
            now.isoformat(),
            now.isoformat() if should_notify else row["last_sent_at"],
            json.dumps(alert, default=str),
            alert["key"],
        ))
        self.conn.commit()
        return should_notify

    def list_alerts(self, limit: int = 200) -> list[dict]:
        rows = self.conn.execute("""
            SELECT alert_key, type, severity, issue_id, project_id, message, status,
                   first_seen_at, last_seen_at, last_sent_at
            FROM alerts
            ORDER BY last_seen_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]

    def insert_metrics(self, ts: datetime, open_issues: int, overdue_issues: int, due_soon_issues: int, project_id: int | None = None) -> None:
        self.conn.execute("""
            INSERT INTO metrics_snapshots(ts, project_id, open_issues, overdue_issues, due_soon_issues)
            VALUES (?, ?, ?, ?, ?)
        """, (ts.isoformat(), project_id, open_issues, overdue_issues, due_soon_issues))
        self.conn.commit()

    def get_metrics(self, limit: int = 200) -> list[dict]:
        rows = self.conn.execute("""
            SELECT ts, project_id, open_issues, overdue_issues, due_soon_issues
            FROM metrics_snapshots
            ORDER BY ts DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]