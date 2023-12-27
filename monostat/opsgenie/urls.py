from django.urls import path, register_converter

from . import views

urlpatterns = [
    path("hook/<str:secret>", views.webhook, name="webhook"),
]
