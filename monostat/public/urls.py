from django.urls import path

from . import views

urlpatterns = [
    path("theme.css", views.ThemeCSSView.as_view(), name="theme.css"),
    path("<str:date>/<int:pk>/", views.IncidentDetailView.as_view(), name="detail"),
    path("", views.IndexView.as_view(), name="index"),
]
