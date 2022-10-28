from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):
    """
    В случае остутствия данных,
    поле будет заполнено словом пусто.
    """

    empty_value_display = '-пусто-'
