from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.core.settings import settings
from datetime import datetime, timedelta, timezone


def decode_and_verify_jwt(token: str) -> dict:
    if not settings.JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET is not configured"
        )
    
    options = {"verify_aud": bool(settings.JWT_AUDIENCE)}
    kwargs = {}

    if settings.JWT_ISSUER:
        kwargs["issuer"] = settings.JWT_ISSUER
    if settings.JWT_AUDIENCE:
        kwargs["audience"] = settings.JWT_AUDIENCE

    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
            options=options,
            **kwargs,
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}"
        )from exc


def create_access_token(claims: dict, expires_minutes: int = 720) -> str:
    if not settings.JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET is not configured"
        )

    now = datetime.now(timezone.utc)
    payload = {
        **claims,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }

    if settings.JWT_ISSUER:
        payload["iss"] = settings.JWT_ISSUER
    if settings.JWT_AUDIENCE:
        payload["aud"] = settings.JWT_AUDIENCE

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)