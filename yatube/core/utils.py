from django.core.paginator import Paginator
from django.http import HttpRequest


def paginate(queryset: list, request: HttpRequest, posts_limit: int) -> None:
    """
    Функция постраничного разделения в зависимости
    от объемов входящей информации,
    вынесена в отдельную область.
    """
    paginator = Paginator(queryset, posts_limit)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
