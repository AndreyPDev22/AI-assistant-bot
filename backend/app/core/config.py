from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    database_url: str = "postgresql+psycopg://localhost:5432/ai_assistant"
    jwt_secret_key: SecretStr
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)
    cookie_secure: bool = False
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


@lru_cache
def get_settings() -> Settings:
    return Settings()
