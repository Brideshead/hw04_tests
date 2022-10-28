from django.urls import path

from about.apps import AboutConfig
from about import views

app_name = AboutConfig.name

urlpatterns = [
    path('author/', views.AboutAuthorView.as_view(), name='author'),
    path('tech/', views.AboutTechView.as_view(), name='tech'),
]
