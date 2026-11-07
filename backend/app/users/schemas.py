from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from fastapi import UploadFile
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Password = Annotated[str, Field(min_length=8, max_length=128)]
Language = Literal["ru", "zh", "en"]
Theme = Literal["dark", "light"]
Notifications = Literal["on", "off"]


class UserSettings(BaseModel):
    language: Language = "ru"
    theme: Theme = "light"
    notifications: Notifications = "off"


class SettingsUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    language: Language | None = None
    theme: Theme | None = None
    notifications: Notifications | None = None

    @model_validator(mode="after")
    def require_values(self):
        if not self.model_fields_set or any(
            getattr(self, field) is None for field in self.model_fields_set
        ):
            raise ValueError("Передайте непустые настройки для обновления")
        return self


class RegisterInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    last_name: Name
    first_name: Name
    middle_name: Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)] = ""
    group: Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^[0-9]{3}-[0-9]{3}$")]
    email: EmailStr = Field(max_length=254)
    password: Password
    photo: UploadFile | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class UserResponse(BaseModel):
    id: UUID
    last_name: str
    first_name: str
    middle_name: str
    group: str
    email: str
    photo_url: str | None
    settings: UserSettings
    created_at: datetime
    updated_at: datetime
