import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_409_CONFLICT,
)

from app.core.config import Settings
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    TokenPair,
    create_access_token,
    decode_access_token,
    hash_refresh_token,
    password_hash,
    token_expiration,
    unauthorized,
)
from app.core.storage import S3PhotoStorage

from app.auth.models import AuthSession, RefreshToken
from app.auth.schemas import LoginInput

from app.users.models import User
from app.users.photos import save_photo
from app.users.schemas import RegisterInput


def issue_tokens(db: Session, auth_session: AuthSession, settings: Settings) -> TokenPair:
    refresh_token = secrets.token_urlsafe(48)
    db.add(
        RefreshToken(
            token_hash=hash_refresh_token(refresh_token),
            session_id=auth_session.id,
        )
    )
    access_expires_at = min(token_expiration(settings), auth_session.expires_at)
    return TokenPair(
        access_token=create_access_token(
            auth_session.user_id,
            auth_session.id,
            access_expires_at,
            settings,
            auth_session.token_version,
        ),
        refresh_token=refresh_token,
        access_expires_at=access_expires_at,
        refresh_expires_at=auth_session.expires_at,
    )


def create_session(db: Session, user: User, settings: Settings) -> TokenPair:
    db.execute(
        delete(AuthSession).where(
            AuthSession.user_id == user.id,
            AuthSession.expires_at <= datetime.now(UTC),
        )
    )
    auth_session = AuthSession(
        id=uuid4(),
        user_id=user.id,
        expires_at=datetime.now(UTC).replace(microsecond=0)
        + timedelta(days=settings.refresh_token_expire_days),
        token_version=0,
    )
    db.add(auth_session)
    db.flush()
    return issue_tokens(db, auth_session, settings)


def register_user(
    db: Session, payload: RegisterInput, storage: S3PhotoStorage, settings: Settings
) -> tuple[User, TokenPair]:
    if db.scalar(select(User.id).where(User.email == payload.email)):
        raise HTTPException(HTTP_409_CONFLICT, "Пользователь с такой почтой уже зарегистрирован")
    user = User(
        email=payload.email,
        password_hash=password_hash.hash(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        middle_name=payload.middle_name,
        group=payload.group,
    )
    photo_key = None
    db.add(user)
    try:
        db.flush()
        photo_key = save_photo(payload.photo, user.id, storage)
        user.photo_key = photo_key
        tokens = create_session(db, user, settings)
        db.commit()
    except Exception as exc:
        db.rollback()
        if photo_key:
            storage.delete_photo(photo_key)
        if (
            isinstance(exc, IntegrityError)
            and getattr(exc.orig, "diag", None)
            and exc.orig.diag.constraint_name == "uq_users_email"
        ):
            raise HTTPException(
                HTTP_409_CONFLICT, "Пользователь с такой почтой уже зарегистрирован"
            ) from exc
        raise
    return user, tokens


def login_user(db: Session, payload: LoginInput, settings: Settings) -> tuple[User, TokenPair]:
    user = db.scalar(select(User).where(User.email == payload.email))
    stored_hash = user.password_hash if user is not None else DUMMY_PASSWORD_HASH
    valid_password, updated_hash = password_hash.verify_and_update(payload.password, stored_hash)
    if user is None or not valid_password or not user.is_active:
        raise HTTPException(HTTP_401_UNAUTHORIZED, "Неверная почта или пароль")
    if updated_hash is not None:
        user.password_hash = updated_hash
    tokens = create_session(db, user, settings)
    db.commit()
    return user, tokens


def refresh_user_session(
    db: Session, token: str | None, settings: Settings
) -> tuple[User, TokenPair]:
    if not token:
        raise unauthorized()
    token_hash = hash_refresh_token(token)
    auth_session = db.scalar(
        select(AuthSession)
        .join(RefreshToken, RefreshToken.session_id == AuthSession.id)
        .where(RefreshToken.token_hash == token_hash)
        .with_for_update(of=AuthSession)
    )
    if auth_session is None:
        raise unauthorized()
    refresh_token = db.get(RefreshToken, token_hash, populate_existing=True)
    user = db.get(User, auth_session.user_id)
    if (
        refresh_token is None
        or refresh_token.used_at is not None
        or auth_session.expires_at <= datetime.now(UTC)
        or user is None
        or not user.is_active
    ):
        db.delete(auth_session)
        db.commit()
        raise unauthorized()
    refresh_token.used_at = datetime.now(UTC)
    auth_session.token_version += 1
    tokens = issue_tokens(db, auth_session, settings)
    db.commit()
    return user, tokens


def revoke_session(
    db: Session, token: str | None, refresh_token: str | None, settings: Settings
) -> None:
    if refresh_token:
        session_id = db.scalar(
            select(RefreshToken.session_id).where(
                RefreshToken.token_hash == hash_refresh_token(refresh_token)
            )
        )
        if session_id:
            db.execute(delete(AuthSession).where(AuthSession.id == session_id))
            db.commit()
            return
    if not token:
        return
    try:
        user_id, session_id, token_version = decode_access_token(token, settings)
    except HTTPException:
        return
    db.execute(
        delete(AuthSession).where(
            AuthSession.id == session_id,
            AuthSession.user_id == user_id,
            AuthSession.token_version == token_version,
        )
    )
    db.commit()
