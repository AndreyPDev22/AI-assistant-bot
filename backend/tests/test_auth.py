from datetime import UTC, datetime, timedelta
from io import BytesIO
from uuid import UUID, uuid4

import jwt
import pytest
from PIL import Image
from sqlalchemy import func, select
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_307_TEMPORARY_REDIRECT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_413_CONTENT_TOO_LARGE,
    HTTP_422_UNPROCESSABLE_CONTENT,
)

from app.core.security import AUDIENCE, COOKIE_NAME, ISSUER, REFRESH_COOKIE_NAME, password_hash

from app.auth.models import AuthSession

from app.users.models import User


def register(client, payload, **kwargs):
    return client.post(
        "/api/users/register",
        files={key: (None, value) for key, value in payload.items()},
        **kwargs,
    )


def signed_token(settings, **changes):
    claims = {
        "sub": str(uuid4()),
        "jti": str(uuid4()),
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(minutes=10),
        "iss": ISSUER,
        "aud": AUDIENCE,
        "type": "access",
    }
    claims.update(changes)
    return jwt.encode(claims, settings.jwt_secret_key.get_secret_value(), algorithm="HS256")


def test_registration_cookie_and_persistence(client, app, registration):
    response = register(client, {**registration, "email": registration["email"].upper()})
    assert response.status_code == HTTP_201_CREATED, response.text
    data = response.json()["data"]
    assert data["email"] == registration["email"]
    assert data["first_name"] == "Иван"
    assert data["photo_url"] is None
    assert "password" not in response.text
    assert response.json()["error"] is None
    cookie = response.headers["set-cookie"]
    assert "HttpOnly" in cookie and "SameSite=lax" in cookie and "Path=/api" in cookie
    access_cookie = next(
        value
        for value in response.headers.get_list("set-cookie")
        if value.startswith(f"{COOKIE_NAME}=")
    )
    max_age = int(access_cookie.split("Max-Age=", 1)[1].split(";", 1)[0])
    assert 0 < max_age <= 1800
    assert REFRESH_COOKIE_NAME in client.cookies
    assert response.headers["cache-control"] == "no-store"
    with app.state.session_factory() as db:
        user = db.get(User, UUID(data["id"]))
        assert user.password_hash.startswith("$argon2id$")
        assert password_hash.verify(registration["password"], user.password_hash)
        assert db.scalar(select(func.count()).select_from(AuthSession)) == 1
    me = client.get("/api/users/me")
    assert me.status_code == HTTP_200_OK
    assert me.json()["data"] == data


def test_duplicate_email_case_insensitive(client, registration):
    assert register(client, registration).status_code == HTTP_201_CREATED
    response = register(client, {**registration, "email": registration["email"].upper()})
    assert response.status_code == HTTP_409_CONFLICT
    assert response.json()["error"]["code"] == HTTP_409_CONFLICT


@pytest.mark.parametrize(
    "changes",
    [
        {"email": "invalid"},
        {"password": "short"},
        {"password": "x" * 129},
        {"group": "261321"},
        {"first_name": "   "},
        {"last_name": "a" * 101},
        {"unexpected": "field"},
    ],
)
def test_invalid_registration_has_no_side_effects(client, app, registration, changes):
    response = register(client, {**registration, **changes})
    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT, response.text
    assert response.json()["data"] is None
    assert all("input" not in detail for detail in response.json()["detail"])
    assert COOKIE_NAME not in client.cookies
    with app.state.session_factory() as db:
        assert db.scalar(select(func.count()).select_from(User)) == 0


def test_registration_requires_fields(client):
    response = client.post("/api/users/register", data={"first_name": "Иван"})
    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT


def test_login_and_independent_sessions(client, app, registration):
    assert register(client, registration).status_code == HTTP_201_CREATED
    original_token = client.cookies[COOKIE_NAME]
    client.cookies.clear()
    response = client.post(
        "/api/auth/login",
        json={
            "email": registration["email"].upper(),
            "password": registration["password"],
        },
    )
    assert response.status_code == HTTP_200_OK, response.text
    assert client.cookies[COOKIE_NAME] != original_token
    assert client.get("/api/users/me").status_code == HTTP_200_OK
    assert client.post("/api/auth/logout").status_code == HTTP_200_OK
    client.cookies.set(COOKIE_NAME, original_token, path="/api", domain="testserver.local")
    assert client.get("/api/users/me").status_code == HTTP_200_OK
    with app.state.session_factory() as db:
        assert db.scalar(select(func.count()).select_from(AuthSession)) == 1


def test_wrong_credentials_have_same_error(client, registration):
    assert register(client, registration).status_code == HTTP_201_CREATED
    client.cookies.clear()
    wrong = client.post(
        "/api/auth/login",
        json={
            "email": registration["email"],
            "password": "wrong password",
        },
    )
    missing = client.post(
        "/api/auth/login",
        json={
            "email": "missing@example.com",
            "password": registration["password"],
        },
    )
    assert wrong.status_code == missing.status_code == HTTP_401_UNAUTHORIZED
    assert wrong.json() == missing.json()
    assert COOKIE_NAME not in client.cookies


def test_logout_revokes_copied_token_and_is_idempotent(client, registration):
    assert register(client, registration).status_code == HTTP_201_CREATED
    token = client.cookies[COOKIE_NAME]
    response = client.post("/api/auth/logout")
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"data": None, "error": None}
    assert COOKIE_NAME not in client.cookies
    client.cookies.set(COOKIE_NAME, token, path="/api", domain="testserver.local")
    assert client.get("/api/users/me").status_code == HTTP_401_UNAUTHORIZED
    assert client.post("/api/auth/logout").status_code == HTTP_200_OK
    assert client.post("/api/auth/logout").status_code == HTTP_200_OK


def test_missing_cookie(client):
    assert client.get("/api/users/me").status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "claims",
    [
        {"exp": datetime.now(UTC) - timedelta(seconds=1)},
        {"iss": "other-app"},
        {"aud": "other-audience"},
        {"type": "refresh"},
        {"sub": "not-a-uuid"},
        {"jti": []},
        {"iat": datetime.now(UTC) + timedelta(hours=1)},
        {},
    ],
)
def test_invalid_claims_or_unknown_session(client, test_settings, claims):
    client.cookies.set(
        COOKIE_NAME, signed_token(test_settings, **claims), path="/api", domain="testserver.local"
    )
    assert client.get("/api/users/me").status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("token", ["not-a-token", "a.b.c"])
def test_malformed_token_and_logout(client, token):
    client.cookies.set(COOKIE_NAME, token, path="/api", domain="testserver.local")
    assert client.get("/api/users/me").status_code == HTTP_401_UNAUTHORIZED
    assert client.post("/api/auth/logout").status_code == HTTP_200_OK
    assert COOKIE_NAME not in client.cookies


def test_tampered_signature(client, registration):
    assert register(client, registration).status_code == HTTP_201_CREATED
    token = client.cookies[COOKIE_NAME]
    header, payload, signature = token.split(".")
    signature = ("a" if signature[0] != "a" else "b") + signature[1:]
    client.cookies.clear()
    client.cookies.set(
        COOKIE_NAME, f"{header}.{payload}.{signature}", path="/api", domain="testserver.local"
    )
    assert client.get("/api/users/me").status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("state", ["inactive", "expired_session", "deleted_user", "wrong_owner"])
def test_database_state_is_checked(client, app, registration, state):
    response = register(client, registration)
    user_id = UUID(response.json()["data"]["id"])
    with app.state.session_factory() as db:
        user = db.get(User, user_id)
        session = db.scalar(select(AuthSession).where(AuthSession.user_id == user_id))
        if state == "inactive":
            user.is_active = False
        elif state == "expired_session":
            session.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        elif state == "deleted_user":
            db.delete(user)
        else:
            other = User(
                email="other@example.com",
                password_hash=user.password_hash,
                first_name="Другой",
                last_name="Пользователь",
                group="261-321",
            )
            db.add(other)
            db.flush()
            session.user_id = other.id
        db.commit()
    assert client.get("/api/users/me").status_code == HTTP_401_UNAUTHORIZED
    if state == "inactive":
        response = client.post(
            "/api/auth/login",
            json={
                "email": registration["email"],
                "password": registration["password"],
            },
        )
        assert response.status_code == HTTP_401_UNAUTHORIZED


def test_csrf_and_cors(client, registration):
    client.headers.pop("X-CSRF-Protection")
    assert register(client, registration).status_code == HTTP_403_FORBIDDEN
    client.headers["X-CSRF-Protection"] = "1"
    assert (
        register(client, registration, headers={"Origin": "https://evil.example"}).status_code
        == HTTP_403_FORBIDDEN
    )
    response = register(client, registration, headers={"Origin": "http://localhost:5173"})
    assert response.status_code == HTTP_201_CREATED
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert response.headers["access-control-allow-credentials"] == "true"
    for origin, expected in [
        ("http://localhost:5173", HTTP_200_OK),
        ("https://evil.example", HTTP_400_BAD_REQUEST),
    ]:
        preflight = client.options(
            "/api/auth/logout",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "X-CSRF-Protection",
            },
        )
        assert preflight.status_code == expected


def test_profile_photo_is_resized_and_private(client, app, registration):
    image = BytesIO()
    Image.new("RGB", (900, 600), "red").save(image, format="PNG")
    files = {key: (None, value) for key, value in registration.items()}
    files["photo"] = ("../../avatar.png", image.getvalue(), "image/png")
    response = client.post("/api/users/register", files=files)
    assert response.status_code == HTTP_201_CREATED, response.text
    photo_url = response.json()["data"]["photo_url"]
    photo = client.get(photo_url, follow_redirects=False)
    assert photo.status_code == HTTP_307_TEMPORARY_REDIRECT
    assert "X-Amz-Signature=" in photo.headers["location"]
    assert photo.headers["cache-control"] == "no-store"
    with app.state.session_factory() as db:
        user = db.get(User, UUID(response.json()["data"]["id"]))
        assert user.photo_key.startswith(f"users/{user.id}/photos/")
        contents = app.state.photo_storage.read_photo(user.photo_key)
    with Image.open(BytesIO(contents)) as decoded:
        assert decoded.size == (512, 341)
    client.cookies.clear()
    assert client.get(photo_url).status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "content, expected_status",
    [
        (b"<svg>fake image</svg>", HTTP_422_UNPROCESSABLE_CONTENT),
        (b"x" * (5 * 1024 * 1024 + 1), HTTP_413_CONTENT_TOO_LARGE),
    ],
)
def test_bad_photo_does_not_create_account(client, app, registration, content, expected_status):
    files = {key: (None, value) for key, value in registration.items()}
    files["photo"] = ("photo.jpg", content, "image/jpeg")
    assert client.post("/api/users/register", files=files).status_code == expected_status
    with app.state.session_factory() as db:
        assert db.scalar(select(func.count()).select_from(User)) == 0


def test_photo_missing(client, registration):
    assert register(client, registration).status_code == HTTP_201_CREATED
    assert client.get("/api/users/me/photo").status_code == HTTP_404_NOT_FOUND


def test_health_and_openapi(client):
    response = client.get("/api/health")
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"data": {"status": "ok"}, "error": None}
    schema = client.get("/openapi.json").json()
    assert schema["components"]["securitySchemes"]["APIKeyHeader"]["name"] == "X-CSRF-Protection"
    assert (
        "multipart/form-data"
        in schema["paths"]["/api/users/register"]["post"]["requestBody"]["content"]
    )
