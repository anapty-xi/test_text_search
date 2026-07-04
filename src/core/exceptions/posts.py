from src.core.exceptions.base import ErrorType, LogicException


class PostsNotFound(LogicException):
    def __init__(self) -> None:
        super().__init__(
            source="query",
            type=ErrorType.NOT_FOUND_ERROR,
            message="Пост не найден",
        )


class PostNotFound(LogicException):
    def __init__(self) -> None:
        super().__init__(
            source="post_id",
            type=ErrorType.NOT_FOUND_ERROR,
            message="Пост не найден",
        )
