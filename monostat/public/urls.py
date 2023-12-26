from django.urls import path

from . import views

urlpatterns = [
    path("theme.css", views.ThemeCSSView.as_view(), name="theme.css"),
    path("", views.IndexView.as_view(), name="index"),
]
