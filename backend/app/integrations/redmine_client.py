import requests
from app.core.config import settings


class RedmineClient:
    def __init__(self):
        self.base_url = settings.REDMINE_URL.rstrip("/")
        self.headers = {
            "X-Redmine-API-Key" : settings.REDMINE_API_KEY,
        }

    def list_users(self) -> list[dict]:
        if not self.base_url or not settings.REDMINE_API_KEY:
            raise RuntimeError("REDMINE_URL / REDMINE_API_KEY not configured")
        
        url = f"{self.base_url}/users.json?status=1&limit=200"
        resp = requests.get(url, headers=self.headers, timeout=20)
        if resp.status_code >= 400:
            raise RuntimeError(f"Redmine API error: {resp.status_code} - {resp.text}")
        
        return resp.json().get("users", [])
    
redmine_client = RedmineClient()