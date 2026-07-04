import logging

from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError

from src.core.exceptions.base import ErrorType
from src.core.exceptions.schemas.detail import ExceptionDetail
from src.core.exceptions.schemas.main import MainException

logger = logging.getLogger(__name__)


async def db_error_handler(request: Request, exc: DBAPIError) -> JSONResponse:
    logger.exception(
        "DB exception: %s %s",
        request.method,
        request.url.path,
        extra={"method": request.method, "path": request.url.path},
    )

    error = ExceptionDetail(
        source="database",
        type=ErrorType.SERVER_ERROR.value,
        message="Ошибка базы данных",
    )

    response = MainException(
        message="Ошибка базы данных",
        errors=[error],
    )

    return JSONResponse(
        status_code=ErrorType.SERVER_ERROR.status_code,
        content=response.model_dump(),
    )
