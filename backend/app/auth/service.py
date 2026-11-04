from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.models import AuthSession
from app.auth.schemas import LoginInput
from app.core.config import Settings
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    create_access_token,
    decode_access_token,
    password_hash,
    token_expiration,
)
from app.users.models import User
from app.users.schemas import RegisterInput, UserResponse


def public_user(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        last_name=user.last_name,
        first_name=user.first_name,
        middle_name=user.middle_name,
        group=user.group,
        email=user.email,
        photo_url="/api/users/me/photo" if user.photo is not None else None,
    )


def create_session(db: Session, user: User, settings: Settings) -> str:
    db.execute(
        delete(AuthSession).where(
            AuthSession.user_id == user.id,
            AuthSession.expires_at <= datetime.now(UTC),
        )
    )
    session_id = uuid4()
    expires_at = token_expiration(settings)
    db.add(AuthSession(id=session_id, user_id=user.id, expires_at=expires_at))
    return create_access_token(user.id, session_id, expires_at, settings)


def register_user(
    db: Session, payload: RegisterInput, photo: bytes | None, settings: Settings
) -> tuple[User, str]:
    if db.scalar(select(User.id).where(User.email == payload.email)):
        raise HTTPException(409, "Пользователь с такой почтой уже зарегистрирован")
    user = User(
        email=payload.email,
        password_hash=password_hash.hash(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        middle_name=payload.middle_name,
        group=payload.group,
        photo=photo,
    )
    db.add(user)
    try:
        db.flush()
        token = create_session(db, user, settings)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if getattr(exc.orig, "diag", None) and exc.orig.diag.constraint_name == "uq_users_email":
            raise HTTPException(409, "Пользователь с такой почтой уже зарегистрирован") from exc
        raise
    return user, token


def login_user(db: Session, payload: LoginInput, settings: Settings) -> tuple[User, str]:
    user = db.scalar(select(User).where(User.email == payload.email))
    stored_hash = user.password_hash if user is not None else DUMMY_PASSWORD_HASH
    valid_password, updated_hash = password_hash.verify_and_update(payload.password, stored_hash)
    if user is None or not valid_password or not user.is_active:
        raise HTTPException(401, "Неверная почта или пароль")
    if updated_hash is not None:
        user.password_hash = updated_hash
    token = create_session(db, user, settings)
    db.commit()
    return user, token


def revoke_session(db: Session, token: str | None, settings: Settings) -> None:
    if not token:
        return
    try:
        user_id, session_id = decode_access_token(token, settings)
    except HTTPException:
        return
    db.execute(
        delete(AuthSession).where(AuthSession.id == session_id, AuthSession.user_id == user_id)
    )
    db.commit()
