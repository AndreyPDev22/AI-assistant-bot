from fastapi import APIRouter, Request, Response

from app.auth.schemas import LoginInput
from app.auth.service import login_user, public_user, revoke_session
from app.core.database import DBSession
from app.core.schemas import Envelope
from app.core.security import COOKIE_NAME, clear_auth_cookie, set_auth_cookie
from app.users.schemas import UserResponse

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/login", response_model=Envelope[UserResponse])
def login(payload: LoginInput, request: Request, response: Response, db: DBSession):
    settings = request.app.state.settings
    user, token = login_user(db, payload, settings)
    set_auth_cookie(response, token, settings)
    return Envelope(data=public_user(user))


@router.post("/logout", response_model=Envelope[None])
def logout(request: Request, response: Response, db: DBSession):
    settings = request.app.state.settings
    revoke_session(db, request.cookies.get(COOKIE_NAME), settings)
    clear_auth_cookie(response, settings)
    return Envelope(data=None)
