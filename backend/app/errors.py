"""User-friendly API error responses without leaking internal details."""

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def _safe_detail(message: str) -> dict[str, str]:
    return {"detail": message}


async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, str):
        return JSONResponse(status_code=exc.status_code, content=_safe_detail(detail))
    return JSONResponse(status_code=exc.status_code, content={"detail": "Request could not be completed."})


async def starlette_http_exception_handler(
    _request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else "Request could not be completed."
    return JSONResponse(status_code=exc.status_code, content=_safe_detail(detail))


async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    message = "Validation failed."
    if exc.errors():
        err = exc.errors()[0]
        msg = err.get("msg", "")
        if msg.startswith("Value error, "):
            msg = msg.removeprefix("Value error, ")
        if msg:
            message = msg
    return JSONResponse(status_code=422, content=_safe_detail(message))


async def unhandled_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=_safe_detail("An unexpected error occurred. Please try again later."),
    )
