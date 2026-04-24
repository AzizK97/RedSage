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

        users: list[dict] = []
        offset = 0
        limit = 100

        while True:
            url = f"{self.base_url}/users.json?status=1&limit={limit}&offset={offset}"
            resp = requests.get(url, headers=self.headers, timeout=20)
            if resp.status_code >= 400:
                raise RuntimeError(f"REDMINE_API_ERROR: {resp.status_code} - {resp.text}")

            payload = resp.json()
            chunk = payload.get("users", [])
            users.extend(chunk)

            total_count = int(payload.get("total_count", len(users)))
            if len(chunk) < limit or len(users) >= total_count:
                break
            offset += limit

        return users

    def get_user(self, redmine_user_id: int) -> dict | None:
        if not self.base_url or not settings.REDMINE_API_KEY:
            raise RuntimeError("REDMINE_URL / REDMINE_API_KEY not configured")

        url = f"{self.base_url}/users/{redmine_user_id}.json?include=groups"
        resp = requests.get(url, headers=self.headers, timeout=20)

        if resp.status_code == 404:
            return None

        if resp.status_code >= 400:
            raise RuntimeError(f"REDMINE_API_ERROR: {resp.status_code} - {resp.text}")

        payload = resp.json()
        return payload.get("user")

    def authenticate_user(self, email_or_login: str, password: str) -> dict | None:
        if not self.base_url:
            raise RuntimeError("REDMINE_URL is not configured")

        identifier = (email_or_login or "").strip()
        if not identifier or not password:
            return None

        user = self._authenticate_with_identifier(identifier, password)
        if user:
            return user

        if "@" in identifier:
            lookup = self._find_user_by_email(identifier)
            login = (lookup or {}).get("login")
            if login:
                return self._authenticate_with_identifier(login, password)
            local_part = identifier.split("@", 1)[0].strip()
            if local_part:
                return self._authenticate_with_identifier(local_part, password)

        return None

    def _authenticate_with_identifier(self, identifier: str, password: str) -> dict | None:
        url = f"{self.base_url}/users/current.json"
        resp = requests.get(url, auth=(identifier, password), timeout=20)

        if resp.status_code == 401:
            return None
        if resp.status_code >= 400:
            raise RuntimeError(f"REDMINE_API_ERROR: {resp.status_code} - {resp.text}")

        return resp.json().get("user")

    def _find_user_by_email(self, email: str) -> dict | None:
        target = email.strip().lower()
        for user in self.list_users():
            if (user.get("mail") or "").strip().lower() == target:
                return user
        return None
    
redmine_client = RedmineClient()