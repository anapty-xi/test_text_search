import logging

from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from src.core.exceptions.base import ErrorType
from src.core.exceptions.schemas.detail import ExceptionDetail
from src.core.exceptions.schemas.main import MainException

logger = logging.getLogger(__name__)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.warning(
        "Validation exception: %s %s",
        request.method,
        request.url.path,
        extra={
            "method": request.method,
            "path": request.url.path,
            "errors": exc.errors(),
        },
    )

    errors = [
        ExceptionDetail(
            source=error["loc"][-1],
            type=ErrorType.VALIDATION_ERROR.value,
            message=error["msg"],
        )
        for error in exc.errors()
    ]

    response = MainException(
        message="Произошла ошибка проверки",
        errors=errors,
    )

    return JSONResponse(
        status_code=ErrorType.VALIDATION_ERROR.status_code,
        content=response.model_dump(),
    )
