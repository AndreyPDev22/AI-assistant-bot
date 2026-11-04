import os
import secrets
from unittest.mock import patch

import pytest
from alembic import command
from alembic.config import Config
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.core.config import BACKEND_DIR, Settings, get_settings
from app.main import create_app


@pytest.fixture(scope="session")
def test_settings():
    env = dotenv_values(BACKEND_DIR / ".env")
    test_url = os.environ.get("TEST_DATABASE_URL") or env.get("TEST_DATABASE_URL")
    if not test_url:
        pytest.fail("Set TEST_DATABASE_URL to a separate PostgreSQL database ending with _test")
    url = make_url(test_url)
    if url.drivername != "postgresql+psycopg" or not (url.database or "").endswith("_test"):
        pytest.fail("TEST_DATABASE_URL must use PostgreSQL and a database name ending with _test")
    production_url = os.environ.get("DATABASE_URL") or env.get("DATABASE_URL")
    if production_url and make_url(production_url) == url:
        pytest.fail("DATABASE_URL and TEST_DATABASE_URL must refer to different databases")
    return Settings(
        _env_file=None,
        database_url=test_url,
        jwt_secret_key=secrets.token_hex(32),
        allowed_origins=["http://localhost:5173", "http://testserver"],
    )


@pytest.fixture(scope="session")
def engine(test_settings):
    with patch.dict(
        os.environ,
        {
            "DATABASE_URL": test_settings.database_url,
            "JWT_SECRET_KEY": test_settings.jwt_secret_key.get_secret_value(),
        },
    ):
        get_settings.cache_clear()
        command.upgrade(Config(str(BACKEND_DIR / "alembic.ini")), "head")
        get_settings.cache_clear()
    engine = create_engine(test_settings.database_url)
    yield engine
    engine.dispose()


@pytest.fixture
def app(engine, test_settings):
    connection = engine.connect()
    transaction = connection.begin()
    application = create_app(test_settings)
    original_engine = application.state.session_factory.kw["bind"]
    application.state.session_factory = sessionmaker(
        bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
    )
    yield application
    transaction.rollback()
    connection.close()
    original_engine.dispose()


@pytest.fixture
def client(app):
    with TestClient(app, headers={"X-CSRF-Protection": "1"}) as client:
        yield client


@pytest.fixture
def registration():
    return {
        "last_name": "Иванов",
        "first_name": "Иван",
        "middle_name": "",
        "group": "261-321",
        "email": f"student-{secrets.token_hex(8)}@example.com",
        "password": "correct password 123",
    }
