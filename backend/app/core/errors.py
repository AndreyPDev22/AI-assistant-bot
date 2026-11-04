import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

logger = logging.getLogger(__name__)


def error_response(status: int, message: str, **kwargs) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"data": None, "error": {"code": status, "message": message}},
        **kwargs,
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
        return error_response(exc.status_code, str(exc.detail), headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]}
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "data": None,
                "error": {"code": 422, "message": "Проверьте данные запроса"},
                "detail": details,
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled %s on %s", type(exc).__name__, request.url.path)
        return error_response(500, "Внутренняя ошибка сервера")
