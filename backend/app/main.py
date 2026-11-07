from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from app.core.config import Settings, get_settings
from app.core.csrf import CSRFMiddleware
from app.core.database import create_session_factory
from app.core.errors import register_error_handlers
from app.core.schemas import Envelope
from app.core.storage import S3PhotoStorage

from app.auth.router import router as auth_router

from app.users.router import router as users_router


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    session_factory = create_session_factory(settings.database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            yield
        finally:
            session_factory.kw["bind"].dispose()
            app.state.photo_storage.close()

    app = FastAPI(
        title="AI Assistant API",
        version="0.1.0",
        lifespan=lifespan,
        dependencies=[
            Depends(
                APIKeyHeader(
                    name="X-CSRF-Protection",
                    auto_error=False,
                    description="Для POST/PUT/PATCH/DELETE нажмите Authorize и введите 1.",
                )
            )
        ],
    )
    app.state.settings = settings
    app.state.session_factory = session_factory
    app.state.photo_storage = S3PhotoStorage(settings)
    register_error_handlers(app)
    app.add_middleware(CSRFMiddleware, allowed_origins=settings.allowed_origins)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "X-CSRF-Protection"],
    )

    @app.middleware("http")
    async def response_headers(request: Request, call_next) -> Response:
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
            response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    app.include_router(auth_router, prefix="/api")
    app.include_router(users_router, prefix="/api")

    @app.get("/api/health", tags=["Служебные"], response_model=Envelope[dict[str, str]])
    def health():
        return Envelope(data={"status": "ok"})

    return app
