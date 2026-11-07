import importlib.util
from uuid import uuid4

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi import HTTPException
from sqlalchemy import inspect, text
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from app.core.config import BACKEND_DIR


def load_migration(filename):
    path = BACKEND_DIR / "migrations" / "versions" / filename
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def legacy_database(engine):
    schema = f"migration_test_{uuid4().hex}"
    with engine.connect() as connection:
        transaction = connection.begin()
        connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
        connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')
        with Operations.context(MigrationContext.configure(connection)):
            load_migration("0001_users_and_sessions.py").upgrade()
            yield connection, schema
        transaction.rollback()


def add_legacy_user(connection, photo, email="legacy@example.com"):
    user_id = uuid4()
    connection.execute(
        text("""
        INSERT INTO users (
            id, email, password_hash, last_name, first_name, middle_name, "group", photo
        )
        VALUES (:id, :email, :password_hash, :last_name, :first_name, :middle_name, :group, :photo)
    """),
        {
            "id": user_id,
            "email": email,
            "password_hash": "existing-hash",
            "last_name": "Иванов",
            "first_name": "Иван",
            "middle_name": "",
            "group": "261-321",
            "photo": photo,
        },
    )
    return user_id


def test_migration_preserves_existing_photos_and_supports_downgrade(
    legacy_database,
    s3,
    test_settings,
    monkeypatch,
):
    connection, schema = legacy_database
    photo = b"existing-jpeg-bytes"
    user_id = add_legacy_user(connection, photo)
    migration = load_migration("0002_profile_storage_and_refresh.py")
    monkeypatch.setattr(migration, "get_settings", lambda: test_settings)
    migration.upgrade()
    user = connection.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id}).one()
    assert user.email == "legacy@example.com" and user.password_hash == "existing-hash"
    assert (user.language, user.theme, user.notifications) == ("ru", "light", "off")
    assert user.updated_at == user.created_at
    assert user.photo_key.startswith(f"users/{user_id}/photos/")
    assert "photo" not in {
        column["name"] for column in inspect(connection).get_columns("users", schema=schema)
    }
    stored = s3.get_object(Bucket=test_settings.s3_bucket, Key=user.photo_key)
    assert stored["Body"].read() == photo
    assert "refresh_tokens" in inspect(connection).get_table_names(schema=schema)
    migration.downgrade()
    restored = connection.execute(
        text("SELECT photo FROM users WHERE id = :id"), {"id": user_id}
    ).scalar_one()
    assert bytes(restored) == photo
    assert "photo_key" not in {
        column["name"] for column in inspect(connection).get_columns("users", schema=schema)
    }
    assert "refresh_tokens" not in inspect(connection).get_table_names(schema=schema)


def test_missing_s3_configuration_does_not_drop_existing_photos(
    legacy_database,
    test_settings,
    monkeypatch,
):
    connection, schema = legacy_database
    photo = b"photo-to-preserve"
    user_id = add_legacy_user(connection, photo)
    migration = load_migration("0002_profile_storage_and_refresh.py")
    monkeypatch.setattr(
        migration,
        "get_settings",
        lambda: test_settings.model_copy(
            update={"s3_bucket": None},
        ),
    )
    savepoint = connection.begin_nested()
    with pytest.raises(HTTPException) as error:
        migration.upgrade()
    assert error.value.status_code == HTTP_503_SERVICE_UNAVAILABLE
    savepoint.rollback()
    columns = {column["name"] for column in inspect(connection).get_columns("users", schema=schema)}
    assert "photo" in columns and "photo_key" not in columns
    restored = connection.execute(
        text("SELECT photo FROM users WHERE id = :id"), {"id": user_id}
    ).scalar_one()
    assert bytes(restored) == photo


def test_partial_photo_migration_cleans_uploaded_objects(
    legacy_database,
    s3,
    test_settings,
    monkeypatch,
):
    connection, schema = legacy_database
    add_legacy_user(connection, b"first-photo")
    add_legacy_user(connection, b"second-photo", email="legacy2@example.com")
    migration = load_migration("0002_profile_storage_and_refresh.py")
    monkeypatch.setattr(migration, "get_settings", lambda: test_settings)
    original = migration.S3PhotoStorage.upload_photo
    calls = 0

    def fail_second_upload(self, contents, user_id):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise HTTPException(HTTP_503_SERVICE_UNAVAILABLE, "Unavailable")
        return original(self, contents, user_id)

    monkeypatch.setattr(migration.S3PhotoStorage, "upload_photo", fail_second_upload)
    savepoint = connection.begin_nested()
    with pytest.raises(HTTPException):
        migration.upgrade()
    savepoint.rollback()
    assert calls == 2
    assert s3.list_objects_v2(Bucket=test_settings.s3_bucket)["KeyCount"] == 0
    assert (
        connection.execute(text("SELECT count(*) FROM users WHERE photo IS NOT NULL")).scalar_one()
        == 2
    )
