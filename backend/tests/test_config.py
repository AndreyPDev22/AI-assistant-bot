import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.core.security import set_auth_cookie


@pytest.mark.parametrize(
    "secret", ["short", "replace-with-a-random-secret-of-at-least-32-characters"]
)
def test_rejects_unsafe_secret(secret):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, jwt_secret_key=secret)


@pytest.mark.parametrize(
    "origin", ["*", "null", "https://example.com/path", "https://example.com/"]
)
def test_rejects_ambiguous_origins(origin):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, jwt_secret_key="s" * 64, allowed_origins=[origin])


def test_secure_cookie_when_configured():
    from fastapi import Response

    response = Response()
    settings = Settings(_env_file=None, jwt_secret_key="s" * 64, cookie_secure=True)
    set_auth_cookie(response, "token", settings)
    assert "Secure" in response.headers["set-cookie"]
