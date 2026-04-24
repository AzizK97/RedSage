from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import Connection

from app.core.security import create_access_token
from app.dependencies.auth import CurrentUser, get_current_user
from app.dependencies.db import get_db
from app.integrations.redmine_client import redmine_client
from app.repositories.entitlement_repository import EntitlementRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, LoginResponse, MeResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


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
    user = users.get_by_redmine_user_id(redmine_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not provisioned on the platform. Contact an admin.",
        )

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
    return LoginResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me(current: CurrentUser = Depends(get_current_user)):
    return MeResponse(
        id=current.id,
        redmine_user_id=current.redmine_user_id,
        role=current.role.value,
        enabled=current.enabled,
    )
