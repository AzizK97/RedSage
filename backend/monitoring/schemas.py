from datetime import datetime, date
from typing import Literal

from pydantic import BaseModel

Severity = Literal["low", "medium", "high", "critical"]
AlertType = Literal["overdue", "due_soon", "stale", "unassigned_high_priority"]

class MonitoringIssue(BaseModel):
    id: int
    project_id: int
    subject: str
    status_id: int
    priority_id: int
    assigned_to_id: int | None = None
    due_date: date | None = None
    updated_on: datetime

class Alert(BaseModel):
    key: str
    type: AlertType
    severity: Severity
    issue_id: int
    project_id: int
    message: str
    detected_at: datetime