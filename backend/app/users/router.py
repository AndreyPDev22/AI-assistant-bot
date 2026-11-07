from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import RedirectResponse
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_307_TEMPORARY_REDIRECT,
    HTTP_404_NOT_FOUND,
)

from app.core.database import DBSession
from app.core.schemas import Envelope
from app.core.security import set_auth_cookies
from app.core.storage import PhotoStorage

from app.auth.dependencies import CurrentUser
from app.auth.service import register_user

from app.users.schemas import RegisterInput, SettingsUpdate, UserResponse, UserSettings
from app.users.service import public_user, update_photo, update_settings

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.post(
    "/register",
    status_code=HTTP_201_CREATED,
    response_model=Envelope[UserResponse],
)
def register(
    payload: Annotated[RegisterInput, Form(media_type="multipart/form-data")],
    request: Request,
    response: Response,
    db: DBSession,
    storage: PhotoStorage,
):
    settings = request.app.state.settings
    user, tokens = register_user(db, payload, storage, settings)
    set_auth_cookies(response, tokens, settings)
    return Envelope(data=public_user(user))


@router.get("/me", response_model=Envelope[UserResponse])
def me(user: CurrentUser):
    return Envelope(data=public_user(user))


@router.patch("/me/settings", response_model=Envelope[UserSettings])
def settings(payload: SettingsUpdate, user: CurrentUser, db: DBSession):
    return Envelope(data=update_settings(db, user, payload))


@router.patch("/me/photo", response_model=Envelope[UserResponse])
def change_photo(
    photo: Annotated[UploadFile, File()],
    user: CurrentUser,
    db: DBSession,
    storage: PhotoStorage,
):
    return Envelope(data=public_user(update_photo(db, user, photo, storage)))


@router.get("/me/photo", response_class=RedirectResponse)
def my_photo(user: CurrentUser, storage: PhotoStorage):
    if user.photo_key is None:
        raise HTTPException(HTTP_404_NOT_FOUND, "Фото не загружено")
    return RedirectResponse(
        storage.photo_url(user.photo_key),
        status_code=HTTP_307_TEMPORARY_REDIRECT,
    )
