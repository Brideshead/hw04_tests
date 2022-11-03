import typing
from datetime import datetime

from django.http import HttpRequest


def year(request: HttpRequest) -> typing.Dict[str, int]:
    """Добавляет переменную с текущим годом."""
    return {
        'year': datetime.now().year,
    }
