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


def test_optional_s3_values_can_be_empty():
    settings = Settings(
        _env_file=None,
        jwt_secret_key="s" * 64,
        s3_bucket="",
        s3_endpoint_url="",
        s3_access_key_id="",
        s3_secret_access_key="",
    )
    assert settings.s3_bucket is None and settings.s3_endpoint_url is None
    assert settings.s3_access_key_id is None and settings.s3_secret_access_key is None


@pytest.mark.parametrize(
    "changes",
    [
        {"s3_access_key_id": "key"},
        {"s3_secret_access_key": "secret"},
        {"s3_endpoint_url": "file:///tmp/bucket"},
        {"s3_endpoint_url": "https://user:password@s3.example.com"},
        {"refresh_token_expire_days": 0},
        {"s3_presigned_url_expire_seconds": 1},
    ],
)
def test_invalid_storage_and_refresh_config(changes):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, jwt_secret_key="s" * 64, **changes)
