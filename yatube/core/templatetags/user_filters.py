from django import template

register = template.Library()


@register.filter
def addclass(field: template, css: None) -> None:
    """
    Пользовательский фильтр для добавления класса к входным данным.
    Позволяет стилизовать выбранную форму.
    """
    return field.as_widget(
        attrs={
            'class': css,
        },
    )
