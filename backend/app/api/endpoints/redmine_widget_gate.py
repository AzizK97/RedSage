"""Server-to-server endpoint for the Redmine plugin to decide whether to render the chat widget."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from psycopg import Connection

from app.core.rbac import Role
from app.core.security import verify_widget_eligibility_bearer_token
from app.dependencies.db import get_db
from app.repositories.entitlement_repository import EntitlementRepository
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/internal", tags=["internal"])


@router.get("/widget-eligibility", include_in_schema=False)
def widget_eligibility(
    redmine_user_id: int = Query(..., ge=1),
    authorization: str = Header(default=""),
    db: Connection = Depends(get_db),
) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    token = authorization.replace("Bearer ", "", 1).strip()
    verify_widget_eligibility_bearer_token(token, redmine_user_id)

    users = UserRepository(db)
    ents = EntitlementRepository(db)
    row = users.get_by_redmine_user_id(redmine_user_id)
    if not row:
        logger.info(
            "widget_eligibility denied redmine_user_id=%s reason=no_row_in_redmine_users",
            redmine_user_id,
        )
        return {"eligible": False}

    role_str = row["platform_role"]
    if role_str not in (Role.ADMIN.value, Role.PROJECT_MANAGER.value):
        logger.info(
            "widget_eligibility denied redmine_user_id=%s reason=role_not_allowed platform_role=%s",
            redmine_user_id,
            role_str,
        )
        return {"eligible": False}

    if not ents.is_enabled(row["id"]):
        logger.info(
            "widget_eligibility denied redmine_user_id=%s reason=entitlement_disabled user_id=%s",
            redmine_user_id,
            row["id"],
        )
        return {"eligible": False}

    return {"eligible": True, "platform_role": role_str}
