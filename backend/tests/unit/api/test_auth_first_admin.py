import pytest

from app.api.endpoints import auth
from app.schemas.auth import LoginRequest


class FakeEntitlements:
    def __init__(self, has_row=False, enabled=False):
        self._has_row = has_row
        self._enabled = enabled
        self.set_calls = []

    def has_access_record(self, user_id):
        return self._has_row

    def set_access(self, user_id, enabled, admin_user_id):
        self.set_calls.append((user_id, enabled, admin_user_id))
        self._has_row = True
        self._enabled = enabled

    def is_enabled(self, user_id):
        return self._enabled


class FakeUsers:
    def __init__(self, existing_user=None):
        self._user = existing_user

    def get_by_redmine_user_id(self, redmine_user_id):
        return self._user

    def mirror_user_from_redmine(self, redmine_user_id, email, full_name, platform_role=None):
        role = platform_role if platform_role is not None else "member"
        self._user = {
            "id": "u-1",
            "redmine_user_id": redmine_user_id,
            "email": email,
            "full_name": full_name or "Admin User",
            "platform_role": role,
        }
        return self._user


class FakeSyncService:
    def __init__(self):
        self.calls = 0

    def sync_all_active_users(self):
        self.calls += 1
        return 42


def test_bootstrap_first_admin_creates_enabled_access_row():
    ents = FakeEntitlements(has_row=False, enabled=False)

    auth._bootstrap_first_admin_access(ents, "u-1", True)

    assert ents.set_calls == [("u-1", True, "system_auto_admin")]
    assert ents.is_enabled("u-1") is True


def test_bootstrap_does_not_override_existing_access_row():
    ents = FakeEntitlements(has_row=True, enabled=False)

    auth._bootstrap_first_admin_access(ents, "u-1", True)

    assert ents.set_calls == []
    assert ents.is_enabled("u-1") is False


def test_login_first_time_admin_is_auto_enabled(monkeypatch):
    monkeypatch.setattr(
        auth.redmine_client,
        "authenticate_user",
        lambda email, password: {
            "id": 1,
            "admin": True,
            "mail": "admin@example.com",
            "firstname": "Admin",
            "lastname": "User",
        },
    )

    fake_users = FakeUsers(existing_user=None)
    fake_ents = FakeEntitlements(has_row=False, enabled=False)
    fake_sync = FakeSyncService()

    monkeypatch.setattr(auth, "UserRepository", lambda db: fake_users)
    monkeypatch.setattr(auth, "EntitlementRepository", lambda db: fake_ents)
    monkeypatch.setattr(auth, "UserSyncService", lambda db: fake_sync)
    monkeypatch.setattr(auth, "create_access_token", lambda payload: "token-123")

    result = auth.login(LoginRequest(email="admin@example.com", password="secret"), db=object())

    assert result.access_token == "token-123"
    assert result.full_name == "Admin User"
    assert fake_ents.set_calls == [("u-1", True, "system_auto_admin")]
    assert fake_sync.calls == 1


def test_login_first_time_non_admin_still_denied(monkeypatch):
    monkeypatch.setattr(
        auth.redmine_client,
        "authenticate_user",
        lambda email, password: {
            "id": 2,
            "admin": False,
            "mail": "member@example.com",
            "firstname": "Member",
            "lastname": "User",
        },
    )

    fake_users = FakeUsers(existing_user=None)
    fake_ents = FakeEntitlements(has_row=False, enabled=False)
    fake_sync = FakeSyncService()

    monkeypatch.setattr(auth, "UserRepository", lambda db: fake_users)
    monkeypatch.setattr(auth, "EntitlementRepository", lambda db: fake_ents)
    monkeypatch.setattr(auth, "UserSyncService", lambda db: fake_sync)

    with pytest.raises(Exception) as exc:
        auth.login(LoginRequest(email="member@example.com", password="secret"), db=object())

    assert getattr(exc.value, "status_code", None) == 403
    assert fake_ents.set_calls == []
    assert fake_sync.calls == 0
