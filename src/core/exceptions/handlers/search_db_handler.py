import logging

from elasticsearch import ApiError, TransportError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from src.core.exceptions.base import ErrorType
from src.core.exceptions.schemas.detail import ExceptionDetail
from src.core.exceptions.schemas.main import MainException

logger = logging.getLogger(__name__)


async def search_db_error_handler(
    request: Request, exc: ApiError | TransportError
) -> JSONResponse:
    logger.exception(
        "Ошибка поисковой базы данных: %s %s",
        request.method,
        request.url.path,
        extra={"method": request.method, "path": request.url.path},
    )

    error = ExceptionDetail(
        source="search_database",
        type=ErrorType.SERVER_ERROR.value,
        message="Ошибка поисковой базы данных",
    )

    response = MainException(
        message="Ошибка поисковой базы данных",
        errors=[error],
    )

    return JSONResponse(
        status_code=ErrorType.SERVER_ERROR.status_code,
        content=response.model_dump(),
    )
