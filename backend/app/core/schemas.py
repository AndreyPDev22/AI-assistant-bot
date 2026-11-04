from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: int
    message: str


class Envelope[T](BaseModel):
    data: T | None = None
    error: ErrorDetail | None = None
