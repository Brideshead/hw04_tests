from django.apps import AppConfig


class AboutConfig(AppConfig):
    """
    Регистрация приложения about.
    Для управления статичными страницами,
    описывающими проект.
    """

    name = 'about'
    verbose_name = 'об приложении'
