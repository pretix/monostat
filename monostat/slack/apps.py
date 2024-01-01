from django.apps import AppConfig


class SlackApp(AppConfig):
    name = "monostat.slack"
    verbose_name = "Slack integration"

    def ready(self):
        from . import incoming  # noqa
