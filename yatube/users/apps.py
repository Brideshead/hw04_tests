from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Регистрация приложения users для управления
    личными данными пользователя.
    """

    name = 'users'
    verbose_name = 'пользователи'
