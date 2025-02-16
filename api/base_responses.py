from domain.entities.models import ErrorResponse

BASE_RESPONSES = {
    200: {
        "description": "Успешный ответ",
    },
    400: {
        "description": "Неверный запрос.",
        "model": ErrorResponse,
    },
    401: {
        "description": "Неавторизован.",
        "model": ErrorResponse,
    },
    422: {
        "description": "Неподдерживаемый контент",
        "model": ErrorResponse,
    },
    500: {
        "description": "Внутренняя ошибка сервера.",
        "model": ErrorResponse,
    },
}
