from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection

from app.dependencies.db import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.entitlement_repository import EntitlementRepository
from app.schemas.auth import LoginRequest, LoginResponse, MeResponse
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Connection = Depends(get_db)):
    user_repo = UserRepository(db)
    ent_repo = EntitlementRepository(db)

    user = user_repo.get_by_email(payload.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not ent_repo.is_enabled(user["id"]) and user["platform_role"] != "admin":
        raise HTTPException(status_code=403, detail="Access disabled by admin")

    token = create_access_token(
        {
            "redmine_user_id": user["redmine_user_id"],
            "role": user["platform_role"],
            "sub": user["id"],
        }
    )
    return LoginResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me():
    raise NotImplementedError("Add current-user lookup using your auth dependency")