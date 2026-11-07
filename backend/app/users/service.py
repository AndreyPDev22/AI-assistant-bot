from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import unauthorized
from app.core.storage import S3PhotoStorage

from app.users.models import User
from app.users.photos import save_photo
from app.users.schemas import SettingsUpdate, UserResponse, UserSettings


def user_settings(user: User) -> UserSettings:
    return UserSettings(
        language=user.language,
        theme=user.theme,
        notifications=user.notifications,
    )


def public_user(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        last_name=user.last_name,
        first_name=user.first_name,
        middle_name=user.middle_name,
        group=user.group,
        email=user.email,
        photo_url=(
            f"/api/users/me/photo?version={user.photo_key.rsplit('/', 1)[-1]}"
            if user.photo_key
            else None
        ),
        settings=user_settings(user),
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def lock_user(db: Session, user_id: UUID) -> User:
    user = db.scalar(
        select(User)
        .where(User.id == user_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if user is None or not user.is_active:
        raise unauthorized()
    return user


def update_settings(db: Session, user: User, payload: SettingsUpdate) -> UserSettings:
    user = lock_user(db, user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user_settings(user)


def update_photo(db: Session, user: User, photo: UploadFile, storage: S3PhotoStorage) -> User:
    user = lock_user(db, user.id)
    old_key = user.photo_key
    new_key = None
    try:
        new_key = save_photo(photo, user.id, storage)
        user.photo_key = new_key
        db.commit()
    except Exception:
        db.rollback()
        if new_key:
            storage.delete_photo(new_key)
        raise
    if old_key:
        storage.delete_photo(old_key)
    db.refresh(user)
    return user
