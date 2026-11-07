import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from fastapi import HTTPException, Response
from pwdlib import PasswordHash
from starlette.status import HTTP_401_UNAUTHORIZED

from app.core.config import Settings

COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"
ALGORITHM = "HS256"
ISSUER = "ai-assistant-backend"
AUDIENCE = "ai-assistant-web"
password_hash = PasswordHash.recommended()
DUMMY_PASSWORD_HASH = password_hash.hash("dummy-password-for-timing-equalization")


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime


def unauthorized() -> HTTPException:
    return HTTPException(HTTP_401_UNAUTHORIZED, "Необходимо войти в аккаунт")


def create_access_token(
    user_id: UUID,
    session_id: UUID,
    expires_at: datetime,
    settings: Settings,
    token_version: int = 0,
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
            "ver": token_version,
        },
        settings.jwt_secret_key.get_secret_value(),
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str, settings: Settings) -> tuple[UUID, UUID, int]:
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
        token_version = payload.get("ver", 0)
        if type(token_version) is not int or token_version < 0:
            raise ValueError("Wrong token version")
        return UUID(payload["sub"]), UUID(payload["jti"]), token_version
    except (jwt.InvalidTokenError, ValueError, TypeError, AttributeError) as exc:
        raise unauthorized() from exc


def token_expiration(settings: Settings) -> datetime:
    return datetime.now(UTC).replace(microsecond=0) + timedelta(
        minutes=settings.access_token_expire_minutes
    )


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def set_auth_cookie(
    response: Response,
    token: str,
    settings: Settings,
    expires_at: datetime | None = None,
) -> None:
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=(
            max(0, int((expires_at - datetime.now(UTC)).total_seconds()))
            if expires_at
            else settings.access_token_expire_minutes * 60
        ),
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/api",
    )


def set_auth_cookies(response: Response, tokens: TokenPair, settings: Settings) -> None:
    set_auth_cookie(response, tokens.access_token, settings, tokens.access_expires_at)
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        tokens.refresh_token,
        max_age=max(0, int((tokens.refresh_expires_at - datetime.now(UTC)).total_seconds())),
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/api/auth",
    )


def clear_auth_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        COOKIE_NAME,
        path="/api",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )
    response.delete_cookie(
        REFRESH_COOKIE_NAME,
        path="/api/auth",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )
