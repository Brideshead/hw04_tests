from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """View-класс для статической страницы author.html."""

    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """View-класс для статической страницы tech.html."""

    template_name = 'about/tech.html'
