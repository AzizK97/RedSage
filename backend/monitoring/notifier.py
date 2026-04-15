import httpx
from .config import settings


async def notify_slack(alert: dict) -> None:
    if not settings.SLACK_WEBHOOK_URL:
        return

    text = f"[{alert['severity'].upper()}] {alert['type']} - {alert['message']} (project={alert['project_id']})"
    payload = {"text": text}

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(settings.SLACK_WEBHOOK_URL, json=payload)
        r.raise_for_status()