import logging

from fastapi.requests import Request
from fastapi.responses import JSONResponse

from src.core.exceptions.base import BaseAPIException
from src.core.exceptions.schemas.detail import ExceptionDetail
from src.core.exceptions.schemas.main import MainException

logger = logging.getLogger(__name__)


async def api_exception_handler(
    request: Request, exc: BaseAPIException
) -> JSONResponse:
    logger.warning(
        "API исключение: %s",
        exc.message,
        extra={
            "method": request.method,
            "path": request.url.path,
            "exception_type": exc.type.value,
            "source": exc.source,
        },
    )

    error = ExceptionDetail(source=exc.source, type=exc.type.value, message=exc.message)

    response = MainException(
        message=exc.message,
        errors=[error],
    )

    return JSONResponse(status_code=exc.status_code, content=response.model_dump())
