import os
import requests
from app.core.config import settings
from datetime import datetime


class RedmineClient:
    def __init__(self):
        self.base_url = settings.REDMINE_URL.rstrip("/")
        self.headers = {
            "X-Redmine-API-Key": settings.REDMINE_API_KEY,
        }

    def _timeout_seconds(self) -> float:
        return float(os.getenv("REDMINE_TIMEOUT_SECONDS", "10"))

    def _json_headers(self) -> dict:
        return {**self.headers, "Content-Type": "application/json"}

    def _send(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Issue an authenticated request and translate transport/HTTP failures
        into the same RuntimeError shapes (REDMINE_UNAVAILABLE / REDMINE_API_ERROR)
        the agent tools have always raised, so prompts and error handling that
        key off those messages keep working unchanged."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method,
                url,
                headers=self._json_headers(),
                timeout=self._timeout_seconds(),
                **kwargs,
            )
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(
                f"REDMINE_UNAVAILABLE: Unable to reach Redmine at '{self.base_url}'. "
                "Make sure Redmine is running and REDMINE_URL is correct."
            ) from exc

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            response_body = (response.text or "").strip()
            raise RuntimeError(
                f"REDMINE_API_ERROR: {method} {endpoint} failed with HTTP {response.status_code}. "
                f"Response: {response_body or 'empty response'}"
            ) from exc

        return response

    def get(self, endpoint: str, params: dict | None = None) -> dict:
        """Generic authenticated GET returning the raw decoded JSON payload.

        Unlike list_projects/list_issues/_paginate, this does not auto-paginate —
        callers (agent tools) keep full control over filters and result limits,
        which they need for ad-hoc, LLM-driven query shapes.
        """
        return self._send("GET", endpoint, params=params or {}).json()

    def post(self, endpoint: str, payload: dict) -> dict:
        """Generic authenticated POST. Returns the decoded JSON payload, or a
        status fallback when Redmine responds with an empty body (e.g. 200)."""
        response = self._send("POST", endpoint, json=payload)
        try:
            return response.json()
        except Exception:
            return {"status": "success", "http_status": response.status_code}

    def put(self, endpoint: str, payload: dict) -> dict:
        """Generic authenticated PUT. Returns the decoded JSON payload, or a
        status fallback when Redmine responds with an empty body (e.g. 200)."""
        response = self._send("PUT", endpoint, json=payload)
        try:
            return response.json()
        except Exception:
            return {"status": "success", "http_status": response.status_code}

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

    def _paginate(self, endpoint: str, array_key: str, params: dict | None = None) -> list[dict]:
        if not self.base_url or not settings.REDMINE_API_KEY:
            raise RuntimeError("REDMINE_URL / REDMINE_API_KEY not configured")

        items: list[dict] = []
        offset = 0
        limit = 100
        query = params.copy() if params else {}

        while True:
            query.update({"limit": limit, "offset": offset})
            url = f"{self.base_url}/{endpoint}"
            resp = requests.get(url, headers=self.headers, params=query, timeout=25)
            if resp.status_code >= 400:
                raise RuntimeError(f"REDMINE_API_ERROR: {resp.status_code} - {resp.text}")

            payload = resp.json()
            chunk = payload.get(array_key, [])
            items.extend(chunk)

            total_count = int(payload.get("total_count", len(items)))
            if len(chunk) < limit or len(items) >= total_count:
                break
            offset += limit

        return items

    def _get_collection(self, endpoint: str, array_key: str) -> list[dict]:
        if not self.base_url or not settings.REDMINE_API_KEY:
            raise RuntimeError("REDMINE_URL / REDMINE_API_KEY not configured")

        url = f"{self.base_url}/{endpoint}"
        resp = requests.get(url, headers=self.headers, timeout=20)
        if resp.status_code >= 400:
            raise RuntimeError(f"REDMINE_API_ERROR: {resp.status_code} - {resp.text}")

        payload = resp.json()
        items = payload.get(array_key, [])
        return items if isinstance(items, list) else []

    def list_projects(self) -> list[dict]:
        return self._paginate("projects.json", "projects")

    def list_issues(self) -> list[dict]:
        return self._paginate(
            "issues.json",
            "issues",
            params={
                "status_id": "*",
                "sort": "updated_on:desc",
            },
        )

    def list_trackers(self) -> list[dict]:
        return self._get_collection("trackers.json", "trackers")

    def list_issue_statuses(self) -> list[dict]:
        return self._get_collection("issue_statuses.json", "issue_statuses")

    def list_issue_priorities(self) -> list[dict]:
        return self._get_collection("enumerations/issue_priorities.json", "issue_priorities")

    def get_project(self, project_id: int | str) -> dict | None:
        if not self.base_url or not settings.REDMINE_API_KEY:
            raise RuntimeError("REDMINE_URL / REDMINE_API_KEY not configured")

        if project_id is None:
            return None

        url = f"{self.base_url}/projects/{project_id}.json"
        resp = requests.get(url, headers=self.headers, timeout=20)
        if resp.status_code == 404:
            return None
        if resp.status_code >= 400:
            raise RuntimeError(f"REDMINE_API_ERROR: {resp.status_code} - {resp.text}")

        payload = resp.json()
        return payload.get("project")

    def get_issue(self, issue_id: int | str) -> dict | None:
        if not self.base_url or not settings.REDMINE_API_KEY:
            raise RuntimeError("REDMINE_URL / REDMINE_API_KEY not configured")

        if issue_id is None:
            return None

        url = f"{self.base_url}/issues/{issue_id}.json"
        resp = requests.get(url, headers=self.headers, timeout=20)
        if resp.status_code == 404:
            return None
        if resp.status_code >= 400:
            raise RuntimeError(f"REDMINE_API_ERROR: {resp.status_code} - {resp.text}")

        payload = resp.json()
        return payload.get("issue")

    def list_project_versions(self, project_identifier: str) -> list[dict]:
        if not project_identifier:
            return []
        return self._get_collection(f"projects/{project_identifier}/versions.json", "versions")

    def list_project_members(self, project_identifier: str) -> list[dict]:
        if not self.base_url or not settings.REDMINE_API_KEY:
            raise RuntimeError("REDMINE_URL / REDMINE_API_KEY not configured")

        if not project_identifier:
            return []

        url = f"{self.base_url}/projects/{project_identifier}/memberships.json"
        resp = requests.get(url, headers=self.headers, timeout=20)
        if resp.status_code >= 400:
            raise RuntimeError(f"REDMINE_API_ERROR: {resp.status_code} - {resp.text}")

        memberships = resp.json().get("memberships", [])
        members: list[dict] = []

        for membership in memberships:
            user = membership.get("user") or {}
            user_id = user.get("id")
            name = (user.get("name") or "").strip()
            if user_id is None or not name:
                continue

            roles = [str(role.get("name", "")).strip() for role in membership.get("roles", [])]
            members.append(
                {
                    "id": user_id,
                    "name": name,
                    "roles": [role for role in roles if role],
                }
            )

        return members

    @staticmethod
    def parse_redmine_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            normalized = value.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized)
        except Exception:
            return None

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

    def list_managed_project_identifiers_for_user(self, redmine_user_id: int) -> list[str]:
        """Return project identifiers for a PM user.

        Prefers projects where the user's membership role looks managerial.
        If none are detected (custom role names, localization), falls back to
        all projects where the user is at least a member.
        """
        managed_identifiers: list[str] = []
        member_identifiers: list[str] = []

        for project in self.list_projects():
            project_identifier = project.get("identifier")
            if not project_identifier:
                continue

            url = f"{self.base_url}/projects/{project_identifier}/memberships.json"
            resp = requests.get(url, headers=self.headers, timeout=20)
            if resp.status_code >= 400:
                raise RuntimeError(f"REDMINE_API_ERROR: {resp.status_code} - {resp.text}")

            memberships = resp.json().get("memberships", [])
            for membership in memberships:
                member_user = membership.get("user") or {}
                if member_user.get("id") != redmine_user_id:
                    continue

                roles = membership.get("roles") or []
                member_identifiers.append(project_identifier)
                has_manager_role = any(
                    any(
                        keyword in str(role.get("name", "")).lower()
                        for keyword in ("manager", "lead", "owner", "chef", "responsable")
                    )
                    for role in roles
                )
                if has_manager_role:
                    managed_identifiers.append(project_identifier)
                break

        source_identifiers = managed_identifiers if managed_identifiers else member_identifiers

        seen: set[str] = set()
        unique_identifiers: list[str] = []
        for identifier in source_identifiers:
            normalized = (identifier or "").strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            unique_identifiers.append(normalized)

        return unique_identifiers

    def list_managed_project_identifiers_for_user_strict(self, redmine_user_id: int) -> list[str]:
        """Return project identifiers where user has a managerial role (no fallback).
        
        Use this for strict PM classification during user sync.
        """
        managed_identifiers: list[str] = []

        for project in self.list_projects():
            project_identifier = project.get("identifier")
            if not project_identifier:
                continue

            url = f"{self.base_url}/projects/{project_identifier}/memberships.json"
            resp = requests.get(url, headers=self.headers, timeout=20)
            if resp.status_code >= 400:
                raise RuntimeError(f"REDMINE_API_ERROR: {resp.status_code} - {resp.text}")

            memberships = resp.json().get("memberships", [])
            for membership in memberships:
                member_user = membership.get("user") or {}
                if member_user.get("id") != redmine_user_id:
                    continue

                roles = membership.get("roles") or []
                has_manager_role = any(
                    any(
                        keyword in str(role.get("name", "")).lower()
                        for keyword in ("manager", "lead", "owner", "chef", "responsable")
                    )
                    for role in roles
                )
                if has_manager_role:
                    managed_identifiers.append(project_identifier)
                break

        seen: set[str] = set()
        unique_identifiers: list[str] = []
        for identifier in managed_identifiers:
            normalized = (identifier or "").strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            unique_identifiers.append(normalized)

        return unique_identifiers

    def list_managed_projects_for_user(self, redmine_user_id: int) -> list[str]:
        """Return project names for a PM user."""
        identifiers = set(self.list_managed_project_identifiers_for_user(redmine_user_id))
        if not identifiers:
            return []
        names: list[str] = []
        for project in self.list_projects():
            identifier = (project.get("identifier") or "").strip()
            if identifier in identifiers:
                names.append((project.get("name") or "").strip())

        return [name for name in names if name]


redmine_client = RedmineClient()