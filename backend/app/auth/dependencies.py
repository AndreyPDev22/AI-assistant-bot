from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, Request

from app.core.database import DBSession
from app.core.security import COOKIE_NAME, decode_access_token, unauthorized

from app.auth.models import AuthSession

from app.users.models import User


def get_current_user(request: Request, db: DBSession) -> User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise unauthorized()
    user_id, session_id, token_version = decode_access_token(token, request.app.state.settings)
    auth_session = db.get(AuthSession, session_id)
    if (
        auth_session is None
        or auth_session.user_id != user_id
        or auth_session.expires_at <= datetime.now(UTC)
        or auth_session.token_version != token_version
    ):
        raise unauthorized()
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise unauthorized()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
