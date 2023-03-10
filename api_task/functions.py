from django.db.models import QuerySet
from rest_framework.request import Request


def filter(qs: QuerySet, request: Request) -> QuerySet:
    """Установка фильтров по данным из GET запроса
    если есть такие атрибуты в модели и установка
    фильтра не вызывает ошибку

    Args:
        qs (QuerySet): Выборка данных
        request (Request): Реквест

    Returns:
        QuerySet: Отфильтрованая выборка данных
    """
    for attr, val in request.query_params.items():
        if hasattr(qs.model, attr):
            if val.lower() in ("none", "null"):
                val = None
            try:
                qs = qs.filter(**{attr: val})
            except Exception:
                pass
    return qs
