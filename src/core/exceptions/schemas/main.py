from pydantic import BaseModel

from src.core.exceptions.schemas.detail import ExceptionDetail


class MainException(BaseModel):
    message: str
    errors: list[ExceptionDetail]
