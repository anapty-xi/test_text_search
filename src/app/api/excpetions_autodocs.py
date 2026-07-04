from typing import Any

from src.core.exceptions.schemas.main import MainException


def error_responses(status_codes: dict[int, str]) -> dict[int | str, dict[str, Any]]:
    """
    Генерирует словарь ответов со схемой MainException для указанных статус-кодов.
    Используется в декораторах эндпоинтов: responses=error_responses(400, 404)
    """
    return {
        str(code): {
            "model": MainException,
            "description": description,
        }
        for code, description in status_codes.items()
    }
