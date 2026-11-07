from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Barrier
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE_CONTENT,
)

from app.core.security import (
    COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    create_access_token,
    hash_refresh_token,
)

from app.auth.models import AuthSession, RefreshToken

from app.users.models import User

from app.main import create_app


def register(client, payload):
    return client.post("/api/users/register", data=payload)


def set_cookie(client, name, value):
    path = "/api/auth" if name == REFRESH_COOKIE_NAME else "/api"
    client.cookies.set(name, value, path=path, domain="testserver.local")


def test_refresh_cookie_is_private_and_hash_only_is_stored(client, app, registration):
    response = register(client, registration)
    assert response.status_code == HTTP_201_CREATED
    token = client.cookies[REFRESH_COOKIE_NAME]
    cookie = next(
        value
        for value in response.headers.get_list("set-cookie")
        if value.startswith(f"{REFRESH_COOKIE_NAME}=")
    )
    assert "HttpOnly" in cookie and "SameSite=lax" in cookie and "Path=/api/auth" in cookie
    assert token not in response.text
    with app.state.session_factory() as db:
        stored = db.get(RefreshToken, hash_refresh_token(token))
        assert stored is not None and stored.used_at is None
        assert len(stored.token_hash) == 64 and stored.token_hash != token
        session = db.get(AuthSession, stored.session_id)
        assert timedelta(days=29) < session.expires_at - datetime.now(UTC) <= timedelta(days=30)


def test_refresh_rotates_both_tokens_and_invalidates_old_access(client, registration):
    assert register(client, registration).status_code == HTTP_201_CREATED
    old_access = client.cookies[COOKIE_NAME]
    old_refresh = client.cookies[REFRESH_COOKIE_NAME]
    response = client.post("/api/auth/refresh")
    assert response.status_code == HTTP_200_OK
    assert client.cookies[COOKIE_NAME] != old_access
    assert client.cookies[REFRESH_COOKIE_NAME] != old_refresh
    assert client.get("/api/auth/me").status_code == HTTP_200_OK
    assert (
        client.get("/api/users/me", headers={"Cookie": f"{COOKIE_NAME}={old_access}"}).status_code
        == HTTP_401_UNAUTHORIZED
    )


def test_expired_access_can_be_refreshed(client, app, test_settings, registration):
    response = register(client, registration)
    user_id = UUID(response.json()["data"]["id"])
    with app.state.session_factory() as db:
        session = db.scalar(select(AuthSession).where(AuthSession.user_id == user_id))
        expired = create_access_token(
            user_id,
            session.id,
            datetime.now(UTC) - timedelta(minutes=1),
            test_settings,
        )
    set_cookie(client, COOKIE_NAME, expired)
    assert client.get("/api/users/me").status_code == HTTP_401_UNAUTHORIZED
    assert client.post("/api/auth/refresh").status_code == HTTP_200_OK
    assert client.get("/api/users/me").status_code == HTTP_200_OK


def test_reused_refresh_revokes_the_entire_session(client, app, registration):
    assert register(client, registration).status_code == HTTP_201_CREATED
    old_refresh = client.cookies[REFRESH_COOKIE_NAME]
    assert client.post("/api/auth/refresh").status_code == HTTP_200_OK
    latest_access = client.cookies[COOKIE_NAME]
    latest_refresh = client.cookies[REFRESH_COOKIE_NAME]
    set_cookie(client, REFRESH_COOKIE_NAME, old_refresh)
    assert client.post("/api/auth/refresh").status_code == HTTP_401_UNAUTHORIZED
    assert COOKIE_NAME not in client.cookies and REFRESH_COOKIE_NAME not in client.cookies
    set_cookie(client, COOKIE_NAME, latest_access)
    set_cookie(client, REFRESH_COOKIE_NAME, latest_refresh)
    assert client.get("/api/users/me").status_code == HTTP_401_UNAUTHORIZED
    assert client.post("/api/auth/refresh").status_code == HTTP_401_UNAUTHORIZED
    with app.state.session_factory() as db:
        assert db.scalar(select(func.count()).select_from(AuthSession)) == 0
        assert db.scalar(select(func.count()).select_from(RefreshToken)) == 0


@pytest.mark.parametrize("token", [None, "unknown-token", "not.a.jwt"])
def test_unknown_refresh_clears_cookies_without_revoking_another_session(
    client, app, registration, token
):
    assert register(client, registration).status_code == HTTP_201_CREATED
    valid_access = client.cookies[COOKIE_NAME]
    client.cookies.clear()
    if token:
        set_cookie(client, REFRESH_COOKIE_NAME, token)
    assert client.post("/api/auth/refresh").status_code == HTTP_401_UNAUTHORIZED
    assert REFRESH_COOKIE_NAME not in client.cookies
    set_cookie(client, COOKIE_NAME, valid_access)
    assert client.get("/api/users/me").status_code == HTTP_200_OK


@pytest.mark.parametrize("state", ["inactive", "expired", "deleted"])
def test_refresh_checks_database_state(client, app, registration, state):
    response = register(client, registration)
    user_id = UUID(response.json()["data"]["id"])
    with app.state.session_factory() as db:
        if state == "inactive":
            db.get(User, user_id).is_active = False
        elif state == "expired":
            session = db.scalar(select(AuthSession).where(AuthSession.user_id == user_id))
            session.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        else:
            db.delete(db.get(User, user_id))
        db.commit()
    assert client.post("/api/auth/refresh").status_code == HTTP_401_UNAUTHORIZED
    assert COOKIE_NAME not in client.cookies and REFRESH_COOKIE_NAME not in client.cookies


def test_logout_revokes_refresh_without_access_cookie(client, registration):
    assert register(client, registration).status_code == HTTP_201_CREATED
    refresh_token = client.cookies[REFRESH_COOKIE_NAME]
    client.cookies.delete(COOKIE_NAME)
    assert client.post("/api/auth/logout").status_code == HTTP_200_OK
    assert REFRESH_COOKIE_NAME not in client.cookies
    set_cookie(client, REFRESH_COOKIE_NAME, refresh_token)
    assert client.post("/api/auth/refresh").status_code == HTTP_401_UNAUTHORIZED


def test_refresh_does_not_extend_absolute_session_lifetime(client, app, registration):
    assert register(client, registration).status_code == HTTP_201_CREATED
    with app.state.session_factory() as db:
        expiration = db.scalar(select(AuthSession.expires_at))
    assert client.post("/api/auth/refresh").status_code == HTTP_200_OK
    assert client.post("/api/auth/refresh").status_code == HTTP_200_OK
    with app.state.session_factory() as db:
        assert db.scalar(select(AuthSession.expires_at)) == expiration


def test_refresh_requires_csrf(client, registration):
    assert register(client, registration).status_code == HTTP_201_CREATED
    token = client.cookies[REFRESH_COOKIE_NAME]
    client.headers.pop("X-CSRF-Protection")
    assert client.post("/api/auth/refresh").status_code == HTTP_403_FORBIDDEN
    assert client.cookies[REFRESH_COOKIE_NAME] == token


@pytest.mark.parametrize("password", ["", "1234567", "x" * 129])
def test_login_requires_password_length_between_8_and_128(client, registration, password):
    response = client.post(
        "/api/auth/login",
        json={
            "email": registration["email"],
            "password": password,
        },
    )
    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT


def test_concurrent_refresh_cannot_use_one_token_twice(engine, test_settings, registration):
    application = create_app(test_settings)
    barrier = Barrier(2)
    user_id = None
    try:
        with TestClient(application, headers={"X-CSRF-Protection": "1"}) as client:
            response = register(client, registration)
            assert response.status_code == HTTP_201_CREATED
            user_id = UUID(response.json()["data"]["id"])
            token = client.cookies[REFRESH_COOKIE_NAME]

            def refresh():
                worker = TestClient(
                    application,
                    headers={
                        "X-CSRF-Protection": "1",
                        "Cookie": f"{REFRESH_COOKIE_NAME}={token}",
                    },
                )
                try:
                    barrier.wait(timeout=10)
                    return worker.post("/api/auth/refresh").status_code
                finally:
                    worker.close()

            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(lambda _: refresh(), range(2)))
            assert sorted(results) == [HTTP_200_OK, HTTP_401_UNAUTHORIZED]
            assert client.get("/api/users/me").status_code == HTTP_401_UNAUTHORIZED
    finally:
        if user_id:
            with engine.begin() as connection:
                connection.execute(delete(User).where(User.id == user_id))
