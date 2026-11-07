from fastapi import APIRouter, HTTPException, Request, Response
from starlette.status import HTTP_401_UNAUTHORIZED

from app.core.database import DBSession
from app.core.errors import error_response
from app.core.schemas import Envelope
from app.core.security import COOKIE_NAME, REFRESH_COOKIE_NAME, clear_auth_cookie, set_auth_cookies

from app.auth.dependencies import CurrentUser
from app.auth.schemas import LoginInput
from app.auth.service import login_user, refresh_user_session, revoke_session

from app.users.schemas import UserResponse
from app.users.service import public_user

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/login", response_model=Envelope[UserResponse])
def login(payload: LoginInput, request: Request, response: Response, db: DBSession):
    settings = request.app.state.settings
    user, tokens = login_user(db, payload, settings)
    set_auth_cookies(response, tokens, settings)
    return Envelope(data=public_user(user))


@router.post("/refresh", response_model=Envelope[UserResponse])
def refresh(request: Request, response: Response, db: DBSession):
    settings = request.app.state.settings
    try:
        user, tokens = refresh_user_session(
            db,
            request.cookies.get(REFRESH_COOKIE_NAME),
            settings,
        )
    except HTTPException as exc:
        if exc.status_code != HTTP_401_UNAUTHORIZED:
            raise
        error = error_response(exc.status_code, str(exc.detail))
        clear_auth_cookie(error, settings)
        return error
    set_auth_cookies(response, tokens, settings)
    return Envelope(data=public_user(user))


@router.get("/me", response_model=Envelope[UserResponse])
def me(user: CurrentUser):
    return Envelope(data=public_user(user))


@router.post("/logout", response_model=Envelope[None])
def logout(request: Request, response: Response, db: DBSession):
    settings = request.app.state.settings
    revoke_session(
        db,
        request.cookies.get(COOKIE_NAME),
        request.cookies.get(REFRESH_COOKIE_NAME),
        settings,
    )
    clear_auth_cookie(response, settings)
    return Envelope(data=None)
