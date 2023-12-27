from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel


def generate_secret():
    return get_random_string(length=64)


class OpsgenieConfiguration(SingletonModel):
    secret = models.CharField(
        max_length=255, verbose_name=_("Webhook secret"), default=generate_secret
    )

    def __str__(self):
        return "OpsGenie Configuration"

    class Meta:
        verbose_name = _("OpsGenie Configuration")
