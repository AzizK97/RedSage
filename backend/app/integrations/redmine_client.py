import requests
from app.core.config import settings


class RedmineClient:
    def __init__(self):
        self.base_url = settings.REDMINE_URL.rstrip("/")
        self.headers = {
            "X-Redmine-API-Key" : settings.REDMINE_API_KEY,
        }

    def _get_paginated(self, path: str, key: str, params: dict | None = None) -> list[dict]:
        if not self.base_url or not settings.REDMINE_API_KEY:
            raise RuntimeError("REDMINE_URL / REDMINE_API_KEY not configured")

        all_items: list[dict] = []
        offset = 0
        limit = 100
        base_params = params.copy() if params else {}

        while True:
            query = {
                **base_params,
                "offset": offset,
                "limit": limit,
            }
            url = f"{self.base_url}{path}"
            resp = requests.get(url, headers=self.headers, params=query, timeout=20)
            if resp.status_code >= 400:
                raise RuntimeError(f"Redmine API error: {resp.status_code} - {resp.text}")

            payload = resp.json()
            items = payload.get(key, [])
            all_items.extend(items)

            total_count = int(payload.get("total_count", len(all_items)))
            offset += len(items)

            if len(items) == 0 or offset >= total_count:
                break

        return all_items

    def list_users(self) -> list[dict]:
        return self._get_paginated("/users.json", "users", params={"status": 1})

    def list_projects(self) -> list[dict]:
        return self._get_paginated("/projects.json", "projects", params={"status": 1})

    def list_project_memberships(self, project_identifier_or_id: str | int) -> list[dict]:
        return self._get_paginated(
            f"/projects/{project_identifier_or_id}/memberships.json",
            "memberships",
        )

    def get_user(self, redmine_user_id: int) -> dict | None:
        if not self.base_url or not settings.REDMINE_API_KEY:
            raise RuntimeError("REDMINE_URL / REDMINE_API_KEY not configured")

        url = f"{self.base_url}/users/{redmine_user_id}.json"
        resp = requests.get(url, headers=self.headers, timeout=20)
        if resp.status_code == 404:
            return None
        if resp.status_code >= 400:
            raise RuntimeError(f"Redmine API error: {resp.status_code} - {resp.text}")

        return resp.json().get("user")
    
redmine_client = RedmineClient()