from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Регистрация служебного приложения core.
    Предназначено для хранения фильтров шаблонов.
    """

    name = 'core'
    verbose_name = 'ядро'
