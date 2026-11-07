from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    database_url: str = "postgresql+psycopg://localhost:5432/ai_assistant"
    jwt_secret_key: SecretStr
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)
    refresh_token_expire_days: int = Field(default=30, ge=1, le=90)
    cookie_secure: bool = False
    s3_bucket: str | None = None
    s3_endpoint_url: str | None = None
    s3_region: str = "us-east-1"
    s3_access_key_id: SecretStr | None = None
    s3_secret_access_key: SecretStr | None = None
    s3_addressing_style: Literal["auto", "path", "virtual"] = "auto"
    s3_presigned_url_expire_seconds: int = Field(default=900, ge=60, le=3600)
    allowed_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if make_url(value).drivername != "postgresql+psycopg":
            raise ValueError("DATABASE_URL must use postgresql+psycopg")
        return value

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_secret(cls, value: SecretStr) -> SecretStr:
        secret = value.get_secret_value()
        if len(secret) < 32 or secret.startswith("replace-with-"):
            raise ValueError("Generate a random JWT_SECRET_KEY with at least 32 characters")
        return value

    @field_validator("allowed_origins")
    @classmethod
    def validate_origins(cls, value: list[str]) -> list[str]:
        from urllib.parse import urlsplit

        for origin in value:
            parsed = urlsplit(origin)
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.netloc
                or parsed.path
                or parsed.query
                or parsed.fragment
                or parsed.username
                or parsed.password
            ):
                raise ValueError("ALLOWED_ORIGINS must contain exact HTTP(S) origins without paths")
        return value

    @field_validator("s3_bucket", "s3_endpoint_url", mode="before")
    @classmethod
    def empty_storage_value(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip() or None
        return value

    @field_validator("s3_endpoint_url")
    @classmethod
    def validate_storage_endpoint(cls, value: str | None) -> str | None:
        from urllib.parse import urlsplit

        if value is not None:
            parsed = urlsplit(value)
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.netloc
                or parsed.username
                or parsed.password
                or parsed.query
                or parsed.fragment
            ):
                raise ValueError("S3_ENDPOINT_URL must be an HTTP(S) URL without credentials")
        return value

    @field_validator("s3_access_key_id", "s3_secret_access_key", mode="before")
    @classmethod
    def empty_storage_secret(cls, value):
        return None if value == "" else value

    @model_validator(mode="after")
    def validate_storage_credentials(self):
        if bool(self.s3_access_key_id) != bool(self.s3_secret_access_key):
            raise ValueError("Set both S3_ACCESS_KEY_ID and S3_SECRET_ACCESS_KEY, or neither")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
