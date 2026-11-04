from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from fastapi import HTTPException, Response
from pwdlib import PasswordHash

from app.core.config import Settings

COOKIE_NAME = "access_token"
ALGORITHM = "HS256"
ISSUER = "ai-assistant-backend"
AUDIENCE = "ai-assistant-web"
password_hash = PasswordHash.recommended()
DUMMY_PASSWORD_HASH = password_hash.hash("dummy-password-for-timing-equalization")


def unauthorized() -> HTTPException:
    return HTTPException(401, "Необходимо войти в аккаунт")


def create_access_token(
    user_id: UUID, session_id: UUID, expires_at: datetime, settings: Settings
) -> str:
    return jwt.encode(
        {
            "sub": str(user_id),
            "jti": str(session_id),
            "iat": datetime.now(UTC),
            "exp": expires_at,
            "iss": ISSUER,
            "aud": AUDIENCE,
            "type": "access",
        },
        settings.jwt_secret_key.get_secret_value(),
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str, settings: Settings) -> tuple[UUID, UUID]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[ALGORITHM],
            issuer=ISSUER,
            audience=AUDIENCE,
            options={"require": ["sub", "jti", "iat", "exp", "iss", "aud", "type"]},
        )
        if payload["type"] != "access":
            raise ValueError("Wrong token type")
        return UUID(payload["sub"]), UUID(payload["jti"])
    except (jwt.InvalidTokenError, ValueError, TypeError, AttributeError) as exc:
        raise unauthorized() from exc


def token_expiration(settings: Settings) -> datetime:
    return datetime.now(UTC).replace(microsecond=0) + timedelta(
        minutes=settings.access_token_expire_minutes
    )


def set_auth_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/api",
    )


def clear_auth_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        COOKIE_NAME,
        path="/api",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )
