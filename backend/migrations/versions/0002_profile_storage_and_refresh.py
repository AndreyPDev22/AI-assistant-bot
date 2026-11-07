import sqlalchemy as sa
from alembic import op

from app.core.config import get_settings
from app.core.storage import S3PhotoStorage

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    op.add_column("users", sa.Column("photo_key", sa.String(1024), nullable=True))
    op.add_column("users", sa.Column("language", sa.String(2), server_default="ru", nullable=False))
    op.add_column("users", sa.Column("theme", sa.String(5), server_default="light", nullable=False))
    op.add_column(
        "users", sa.Column("notifications", sa.String(3), server_default="off", nullable=False)
    )
    op.add_column(
        "users",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.execute("UPDATE users SET updated_at = created_at")
    op.create_check_constraint(op.f("ck_users_language"), "users", "language IN ('ru', 'zh', 'en')")
    op.create_check_constraint(op.f("ck_users_theme"), "users", "theme IN ('dark', 'light')")
    op.create_check_constraint(
        op.f("ck_users_notifications"),
        "users",
        "notifications IN ('on', 'off')",
    )
    op.add_column(
        "auth_sessions",
        sa.Column(
            "token_version",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["auth_sessions.id"],
            name="fk_refresh_tokens_session_id_auth_sessions",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("token_hash", name="pk_refresh_tokens"),
    )
    op.create_index("ix_refresh_tokens_session_id", "refresh_tokens", ["session_id"])
    storage = S3PhotoStorage(get_settings())
    uploaded = []
    try:
        for user in connection.execute(
            sa.text("SELECT id, photo FROM users WHERE photo IS NOT NULL")
        ):
            key = storage.upload_photo(bytes(user.photo), user.id)
            uploaded.append(key)
            connection.execute(
                sa.text("UPDATE users SET photo_key = :key WHERE id = :user_id"),
                {"key": key, "user_id": user.id},
            )
        op.drop_column("users", "photo")
        op.execute("""
            CREATE FUNCTION set_user_updated_at() RETURNS trigger AS $$
            BEGIN
                NEW.updated_at = clock_timestamp();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql
        """)
        op.execute("""
            CREATE TRIGGER users_updated_at BEFORE UPDATE ON users
            FOR EACH ROW EXECUTE FUNCTION set_user_updated_at()
        """)
    except Exception:
        for key in uploaded:
            storage.delete_photo(key)
        raise


def downgrade() -> None:
    connection = op.get_bind()
    op.add_column("users", sa.Column("photo", sa.LargeBinary(), nullable=True))
    storage = S3PhotoStorage(get_settings())
    for user in connection.execute(
        sa.text("SELECT id, photo_key FROM users WHERE photo_key IS NOT NULL")
    ):
        photo = storage.read_photo(user.photo_key)
        connection.execute(
            sa.text("UPDATE users SET photo = :photo WHERE id = :user_id"),
            {"photo": photo, "user_id": user.id},
        )
    op.execute("DROP TRIGGER users_updated_at ON users")
    op.execute("DROP FUNCTION set_user_updated_at()")
    op.drop_table("refresh_tokens")
    op.drop_column("auth_sessions", "token_version")
    for constraint in ("ck_users_language", "ck_users_theme", "ck_users_notifications"):
        op.drop_constraint(op.f(constraint), "users", type_="check")
    for column in ("photo_key", "language", "theme", "notifications", "updated_at"):
        op.drop_column("users", column)
