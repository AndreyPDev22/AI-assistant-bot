from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.errors import error_response


class CSRFMiddleware:
    def __init__(self, app: ASGIApp, allowed_origins: list[str]) -> None:
        self.app = app
        self.allowed_origins = set(allowed_origins)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] == "http"
            and scope["path"].startswith("/api/")
            and scope["method"] not in {"GET", "HEAD", "OPTIONS"}
        ):
            headers = dict(scope["headers"])
            origin = headers.get(b"origin")
            if headers.get(b"x-csrf-protection") != b"1" or (
                origin is not None and origin.decode("latin-1") not in self.allowed_origins
            ):
                response = error_response(403, "Запрос не прошёл проверку CSRF")
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)
