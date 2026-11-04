from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request, Response

from app.auth.dependencies import CurrentUser
from app.auth.service import public_user, register_user
from app.core.database import DBSession
from app.core.schemas import Envelope
from app.core.security import set_auth_cookie
from app.users.photos import read_photo
from app.users.schemas import RegisterInput, UserResponse

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.post("/register", status_code=201, response_model=Envelope[UserResponse])
def register(
    payload: Annotated[RegisterInput, Form(media_type="multipart/form-data")],
    request: Request,
    response: Response,
    db: DBSession,
):
    settings = request.app.state.settings
    user, token = register_user(db, payload, read_photo(payload.photo), settings)
    set_auth_cookie(response, token, settings)
    return Envelope(data=public_user(user))


@router.get("/me", response_model=Envelope[UserResponse])
def me(user: CurrentUser):
    return Envelope(data=public_user(user))


@router.get("/me/photo", response_class=Response)
def my_photo(user: CurrentUser):
    if user.photo is None:
        raise HTTPException(404, "Фото не загружено")
    return Response(content=user.photo, media_type="image/jpeg")
