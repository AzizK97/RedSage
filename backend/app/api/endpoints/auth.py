from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from psycopg import Connection
from urllib.parse import urlencode
import requests

from app.core.settings import get_settings

from app.core.security import create_access_token
from app.dependencies.auth import CurrentUser, get_current_user
from app.dependencies.db import get_db
from app.integrations.redmine_client import redmine_client
from app.repositories.entitlement_repository import EntitlementRepository
from app.repositories.user_repository import UserRepository
from app.services.user_sync_service import UserSyncService
from app.schemas.auth import LoginRequest, LoginResponse, MeResponse, RedmineConnectRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _json_or_400(resp: requests.Response, context: str) -> dict:
    try:
        payload = resp.json()
    except ValueError:
        content_type = resp.headers.get("content-type", "unknown")
        snippet = (resp.text or "").strip().replace("\n", " ")[:220]
        if not snippet:
            snippet = "<empty body>"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"{context} returned non-JSON response "
                f"(status={resp.status_code}, content-type={content_type}). "
                f"Body starts with: {snippet}"
            ),
        )

    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{context} returned unexpected JSON shape (expected object)",
        )

    return payload


def _bootstrap_first_admin_access(ents: EntitlementRepository, user_id: str, is_admin: bool) -> None:
    if not is_admin:
        return
    if ents.has_access_record(user_id):
        return
    ents.set_access(user_id, True, admin_user_id="system_auto_admin")


def _sync_directory_if_admin(db: Connection, is_admin: bool) -> None:
    if not is_admin:
        return
    UserSyncService(db).sync_all_active_users()


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Connection = Depends(get_db)):
    redmine_user = redmine_client.authenticate_user(payload.email, payload.password)
    if not redmine_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Invalid Redmine credentials. Use your Redmine username or email + password. "
                "If credentials are correct, verify Redmine REST API authentication is enabled."
            ),
        )

    redmine_user_id = int(redmine_user.get("id", 0))
    if redmine_user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to resolve Redmine user identity",
        )

    users = UserRepository(db)
    ents = EntitlementRepository(db)
    # Detect Redmine admin and promote on login if needed (hybrid safe mode)
    try:
        is_admin = bool(redmine_user.get("admin"))
    except Exception:
        is_admin = False

    user = users.get_by_redmine_user_id(redmine_user_id)
    if not user:
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not provisioned on the platform. Contact an admin.",
            )
        user = users.mirror_user_from_redmine(
            redmine_user_id,
            redmine_user.get("mail", ""),
            " ".join([redmine_user.get("firstname", ""), redmine_user.get("lastname", "")]).strip(),
            "admin",
        )

    if user:
        # Update email/full_name and promote to admin if Redmine indicates admin.
        user = users.mirror_user_from_redmine(redmine_user_id, redmine_user.get("mail", ""),
                                             " ".join([redmine_user.get("firstname", ""), redmine_user.get("lastname", "")]).strip(),
                                             "admin" if is_admin else None)

    _bootstrap_first_admin_access(ents, user["id"], is_admin)
    _sync_directory_if_admin(db, is_admin)

    enabled = ents.is_enabled(user["id"])
    if not enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access disabled by Admin",
        )

    token = create_access_token(
        {
            "sub": user["id"],
            "redmine_user_id": user["redmine_user_id"],
            "role": user["platform_role"],
            "email": user["email"],
        }
    )
    return LoginResponse(access_token=token, full_name=user["full_name"])


@router.get("/me", response_model=MeResponse)
def me(current: CurrentUser = Depends(get_current_user)):
    return MeResponse(
        id=current.id,
        redmine_user_id=current.redmine_user_id,
        role=current.role.value,
        enabled=current.enabled,
    )


# --- Redmine OAuth flow (per-user) ---


@router.get("/redmine/authorize")
def redmine_authorize(request: Request):
    settings = get_settings()
    if not settings.REDMINE_OAUTH_CLIENT_ID:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Redmine OAuth is not configured")

    authorize_base = settings.REDMINE_OAUTH_AUTHORIZE_URL or f"{settings.REDMINE_URL.rstrip('/')}/oauth/authorize"
    redirect_uri = (
        settings.REDMINE_OAUTH_REDIRECT_URI
        or f"{str(request.base_url).rstrip('/')}{settings.REDMINE_OAUTH_REDIRECT_PATH}"
    )

    params = {
        "client_id": settings.REDMINE_OAUTH_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
    }
    if settings.REDMINE_OAUTH_SCOPES:
        params["scope"] = " ".join(settings.REDMINE_OAUTH_SCOPES)

    url = f"{authorize_base}?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/redmine/callback", name="redmine_callback", response_model=LoginResponse)
def redmine_callback(request: Request, code: str | None = None, db: Connection = Depends(get_db)):
    settings = get_settings()
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing authorization code")

    token_url = settings.REDMINE_OAUTH_TOKEN_URL or f"{settings.REDMINE_URL.rstrip('/')}/oauth/token"
    redirect_uri = settings.REDMINE_OAUTH_REDIRECT_URI or f"{str(request.base_url).rstrip('/')}{settings.REDMINE_OAUTH_REDIRECT_PATH}"

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.REDMINE_OAUTH_CLIENT_ID,
        "client_secret": settings.REDMINE_OAUTH_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
    }

    resp = requests.post(token_url, data=data, timeout=20)
    if resp.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Token exchange failed: {resp.text}")

    token_payload = _json_or_400(resp, "Redmine token endpoint")
    access_token = token_payload.get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No access token returned by Redmine")

    # Fetch current user from Redmine with the received token
    user_resp = requests.get(f"{settings.REDMINE_URL.rstrip('/')}/users/current.json", headers={"Authorization": f"Bearer {access_token}"}, timeout=20)
    if user_resp.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to fetch Redmine user: {user_resp.text}")

    user_payload = _json_or_400(user_resp, "Redmine current-user endpoint")
    user_obj = user_payload.get("user")
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to resolve Redmine user information")

    redmine_user_id = int(user_obj.get("id", 0))
    email = user_obj.get("mail") or ""
    full_name = " ".join([user_obj.get("firstname", ""), user_obj.get("lastname", "")]).strip()

    users = UserRepository(db)
    ents = EntitlementRepository(db)
    is_admin = bool(user_obj.get("admin"))
    local_user = users.mirror_user_from_redmine(redmine_user_id, email, full_name, "admin" if is_admin else None)
    _bootstrap_first_admin_access(ents, local_user["id"], is_admin)
    _sync_directory_if_admin(db, is_admin)

    enabled = ents.is_enabled(local_user["id"])
    if not enabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access disabled by Admin")

    token = create_access_token(
        {
            "sub": local_user["id"],
            "redmine_user_id": local_user["redmine_user_id"],
            "role": local_user["platform_role"],
            "email": local_user["email"],
        }
    )

    # If frontend redirect is configured, send user back to SPA with token in fragment.
    frontend = settings.REDMINE_OAUTH_FRONTEND_REDIRECT.strip()
    if frontend:
        # Build redirect target: <frontend>/auth/redmine/callback#token=...&full_name=...
        base = frontend.rstrip("/")
        fragment = urlencode({"token": token, "full_name": local_user.get("full_name", "")})
        url = f"{base}/auth/redmine/callback#{fragment}"
        return RedirectResponse(url)

    # Fallback: return JSON payload
    return LoginResponse(access_token=token, full_name=local_user["full_name"])


@router.post("/redmine/connect", response_model=LoginResponse)
def redmine_connect(payload: RedmineConnectRequest, db: Connection = Depends(get_db)):
    settings = get_settings()

    base = (payload.redmine_url or settings.REDMINE_URL or "").rstrip("/")
    if not base:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Redmine base URL is required")

    api_key = (payload.api_key or "").strip()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="API key is required")

    # Try X-Redmine-API-Key first (typical), fall back to Bearer
    headers = {"X-Redmine-API-Key": api_key}
    user_resp = requests.get(f"{base}/users/current.json", headers=headers, timeout=20)
    if user_resp.status_code == 401:
        # Try Bearer authorization
        user_resp = requests.get(f"{base}/users/current.json", headers={"Authorization": f"Bearer {api_key}"}, timeout=20)

    if user_resp.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to fetch Redmine user: {user_resp.text}")

    user_payload = _json_or_400(user_resp, "Redmine current-user endpoint")
    user_obj = user_payload.get("user")
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to resolve Redmine user information")

    redmine_user_id = int(user_obj.get("id", 0))
    email = user_obj.get("mail") or ""
    full_name = " ".join([user_obj.get("firstname", ""), user_obj.get("lastname", "")]).strip()

    users = UserRepository(db)
    ents = EntitlementRepository(db)
    is_admin = bool(user_obj.get("admin"))
    local_user = users.mirror_user_from_redmine(redmine_user_id, email, full_name, "admin" if is_admin else None)
    _bootstrap_first_admin_access(ents, local_user["id"], is_admin)
    _sync_directory_if_admin(db, is_admin)

    enabled = ents.is_enabled(local_user["id"])
    if not enabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access disabled by Admin")

    token = create_access_token(
        {
            "sub": local_user["id"],
            "redmine_user_id": local_user["redmine_user_id"],
            "role": local_user["platform_role"],
            "email": local_user["email"],
        }
    )

    return LoginResponse(access_token=token, full_name=local_user["full_name"])
