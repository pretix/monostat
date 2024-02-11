from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel


def generate_secret():
    return get_random_string(length=64)


class SlackConfiguration(SingletonModel):
    bot_token = models.CharField(
        max_length=255, verbose_name=_("Bot token"), default=generate_secret
    )
    signing_secret = models.CharField(
        max_length=255, verbose_name=_("Signing secret"), default=generate_secret
    )
    channel_name = models.CharField(
        max_length=255,
        verbose_name=_("Channel name"),
    )
    channel_id = models.CharField(
        max_length=255,
        verbose_name=_("Channel ID"),
        help_text=_("Will be filled automatically!"),
        blank=True,
        null=True,
    )

    def __str__(self):
        return "Slack Configuration"

    class Meta:
        verbose_name = _("Slack Configuration")
