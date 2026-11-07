from io import BytesIO
from uuid import UUID

import pytest
from botocore.exceptions import ClientError
from PIL import Image
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
    HTTP_422_UNPROCESSABLE_CONTENT,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from app.auth.models import AuthSession

from app.users.models import User


def register(client, payload):
    return client.post("/api/users/register", data=payload)


def image_upload(color="red"):
    image = BytesIO()
    Image.new("RGB", (800, 600), color).save(image, format="PNG")
    return ("avatar.png", image.getvalue(), "image/png")


def test_default_settings_and_profile_alias(client, registration):
    response = register(client, registration)
    assert response.status_code == HTTP_201_CREATED
    user = response.json()["data"]
    assert user["settings"] == {"language": "ru", "theme": "light", "notifications": "off"}
    assert user["created_at"] and user["updated_at"]
    assert client.get("/api/auth/me").json()["data"] == user
    assert client.get("/api/users/me").json()["data"] == user


@pytest.mark.parametrize(
    "changes",
    [
        {"language": "zh"},
        {"language": "en"},
        {"theme": "dark"},
        {"notifications": "on"},
        {"language": "en", "theme": "dark", "notifications": "on"},
    ],
)
def test_settings_are_persisted_and_updated_at_changes(client, app, registration, changes):
    response = register(client, registration)
    user = response.json()["data"]
    updated = client.patch("/api/users/me/settings", json=changes)
    assert updated.status_code == HTTP_200_OK
    assert updated.json()["data"] == {**user["settings"], **changes}
    restored = client.get("/api/auth/me").json()["data"]
    assert restored["settings"] == updated.json()["data"]
    assert restored["created_at"] == user["created_at"]
    assert restored["updated_at"] > user["updated_at"]
    with app.state.session_factory() as db:
        stored = db.get(User, UUID(user["id"]))
        for key, value in changes.items():
            assert getattr(stored, key) == value


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"language": "fr"},
        {"theme": "blue"},
        {"notifications": True},
        {"language": None},
        {"theme": None},
        {"notifications": None},
        {"is_active": False},
        {"settings": {"language": "en"}},
    ],
)
def test_invalid_settings_do_not_change_profile(client, registration, payload):
    initial = register(client, registration).json()["data"]
    response = client.patch("/api/users/me/settings", json=payload)
    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    assert client.get("/api/users/me").json()["data"] == initial


def test_settings_require_authentication(client):
    assert (
        client.patch("/api/users/me/settings", json={"theme": "dark"}).status_code
        == HTTP_401_UNAUTHORIZED
    )
    assert (
        client.patch("/api/users/me/photo", files={"photo": image_upload()}).status_code
        == HTTP_401_UNAUTHORIZED
    )


def test_photo_replacement_stores_key_and_deletes_old_object(
    client, app, s3, test_settings, registration
):
    initial = register(client, registration).json()["data"]
    first = client.patch("/api/users/me/photo", files={"photo": image_upload()})
    assert first.status_code == HTTP_200_OK
    with app.state.session_factory() as db:
        first_key = db.get(User, UUID(initial["id"])).photo_key
    second = client.patch("/api/users/me/photo", files={"photo": image_upload("blue")})
    assert second.status_code == HTTP_200_OK
    assert second.json()["data"]["photo_url"] != first.json()["data"]["photo_url"]
    assert second.json()["data"]["updated_at"] > initial["updated_at"]
    objects = s3.list_objects_v2(Bucket=test_settings.s3_bucket).get("Contents", [])
    assert len(objects) == 1 and objects[0]["Key"] != first_key
    with app.state.session_factory() as db:
        stored = db.get(User, UUID(initial["id"]))
        assert stored.photo_key == objects[0]["Key"]
        assert isinstance(stored.photo_key, str)
        contents = app.state.photo_storage.read_photo(stored.photo_key)
    with Image.open(BytesIO(contents)) as photo:
        assert photo.format == "JPEG" and photo.size == (512, 384)


def test_failed_s3_upload_does_not_create_user(client, app, registration, monkeypatch):
    def fail_upload(**kwargs):
        raise ClientError(
            {"Error": {"Code": "ServiceUnavailable", "Message": "offline"}}, "PutObject"
        )

    monkeypatch.setattr(app.state.photo_storage.client, "put_object", fail_upload)
    files = {key: (None, value) for key, value in registration.items()}
    files["photo"] = image_upload()
    response = client.post("/api/users/register", files=files)
    assert response.status_code == HTTP_503_SERVICE_UNAVAILABLE
    with app.state.session_factory() as db:
        assert db.scalar(select(User).where(User.email == registration["email"])) is None
        assert db.scalar(select(AuthSession)) is None


def test_unconfigured_s3_allows_registration_without_photo(client, app, registration):
    app.state.photo_storage.settings = app.state.settings.model_copy(update={"s3_bucket": None})
    assert register(client, registration).status_code == HTTP_201_CREATED
    response = client.patch("/api/users/me/photo", files={"photo": image_upload()})
    assert response.status_code == HTTP_503_SERVICE_UNAVAILABLE
    assert client.get("/api/users/me").json()["data"]["photo_url"] is None


def test_db_failure_removes_uploaded_photo(
    client, app, s3, test_settings, registration, monkeypatch
):
    def fail_commit(self):
        raise RuntimeError("simulated commit failure")

    monkeypatch.setattr(Session, "commit", fail_commit)
    files = {key: (None, value) for key, value in registration.items()}
    files["photo"] = image_upload()
    with pytest.raises(RuntimeError, match="simulated commit failure"):
        client.post("/api/users/register", files=files)
    assert s3.list_objects_v2(Bucket=test_settings.s3_bucket).get("KeyCount") == 0
    with app.state.session_factory() as db:
        assert db.scalar(select(User).where(User.email == registration["email"])) is None


def test_failed_photo_replacement_preserves_old_photo(
    client,
    app,
    s3,
    test_settings,
    registration,
    monkeypatch,
):
    user_id = UUID(register(client, registration).json()["data"]["id"])
    assert (
        client.patch("/api/users/me/photo", files={"photo": image_upload()}).status_code
        == HTTP_200_OK
    )
    with app.state.session_factory() as db:
        old_key = db.get(User, user_id).photo_key

    def fail_commit(self):
        raise RuntimeError("simulated commit failure")

    monkeypatch.setattr(Session, "commit", fail_commit)
    with pytest.raises(RuntimeError, match="simulated commit failure"):
        client.patch("/api/users/me/photo", files={"photo": image_upload("blue")})
    objects = s3.list_objects_v2(Bucket=test_settings.s3_bucket)["Contents"]
    assert [item["Key"] for item in objects] == [old_key]
    with app.state.session_factory() as db:
        assert db.get(User, user_id).photo_key == old_key


def test_new_schema_and_database_constraints(engine, client, app, registration):
    columns = {column["name"] for column in inspect(engine).get_columns("users")}
    assert "photo" not in columns
    assert {"photo_key", "updated_at", "language", "theme", "notifications"} <= columns
    response = register(client, registration)
    with app.state.session_factory() as db:
        user = db.get(User, UUID(response.json()["data"]["id"]))
        user.language = "fr"
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()


def test_updated_at_changes_for_direct_sql_updates(client, app, registration):
    initial = register(client, registration).json()["data"]
    with app.state.session_factory() as db:
        db.execute(
            text("UPDATE users SET first_name = :name WHERE id = :id"),
            {
                "name": "Новое имя",
                "id": UUID(initial["id"]),
            },
        )
        db.commit()
    updated = client.get("/api/users/me").json()["data"]
    assert updated["first_name"] == "Новое имя"
    assert updated["updated_at"] > initial["updated_at"]
