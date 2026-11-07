from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("language IN ('ru', 'zh', 'en')", name="language"),
        CheckConstraint("theme IN ('dark', 'light')", name="theme"),
        CheckConstraint("notifications IN ('on', 'off')", name="notifications"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(100))
    first_name: Mapped[str] = mapped_column(String(100))
    middle_name: Mapped[str] = mapped_column(String(100), default="")
    group: Mapped[str] = mapped_column(String(7))
    photo_key: Mapped[str | None] = mapped_column(String(1024))
    language: Mapped[str] = mapped_column(String(2), default="ru", server_default="ru")
    theme: Mapped[str] = mapped_column(String(5), default="light", server_default="light")
    notifications: Mapped[str] = mapped_column(String(3), default="off", server_default="off")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
