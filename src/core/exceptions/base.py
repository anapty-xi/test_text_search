from enum import Enum
from uuid import uuid4


class ErrorType(Enum):
    """Типы ошибок API."""

    INPUT_ERROR = ("INPUT_ERROR", 400)
    LOGIC_ERROR = ("LOGIC_ERROR", 400)
    SERVER_ERROR = ("SERVER_ERROR", 500)
    VALIDATION_ERROR = ("VALIDATION_ERROR", 422)
    NOT_FOUND_ERROR = ("NOT_FOUND_ERROR", 404)
    CONFLICT_ERROR = ("CONFLICT_ERROR", 409)

    def __new__(cls, value: str, status_code: int) -> "ErrorType":
        obj = object.__new__(cls)
        obj._value_ = value
        obj.status_code = status_code
        return obj

    _value_: str
    status_code: int


class BaseAPIException(Exception):
    def __init__(self, source: str, type: ErrorType, message: str):
        self.source = source
        self.type = type
        self.message = message
        self.error_id = uuid4()
        super().__init__(self.message)

    @property
    def status_code(self) -> int:
        """HTTP статус код из типа ошибки."""
        return self.type.status_code


class InputException(BaseAPIException):
    pass


class LogicException(BaseAPIException):
    pass


class ServerException(BaseAPIException):
    pass
