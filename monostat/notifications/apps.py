from django.apps import AppConfig


class NotificationsApp(AppConfig):
    name = "monostat.notifications"
    verbose_name = "Notifications"

    def ready(self):
        from . import tasks  # noqa
