from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel


def generate_token():
    return get_random_string(length=16)


class NotificationConfiguration(SingletonModel):
    reply_to = models.EmailField(verbose_name=_("Reply-to address"))
    allow_subscriptions = models.BooleanField(
        verbose_name=_("Allow new subscriptions"), default=False
    )

    def __str__(self):
        return "Notification Configuration"

    class Meta:
        verbose_name = _("Notification Configuration")


class Subscriber(models.Model):
    email = models.EmailField(verbose_name=_("Email address"))
    active = models.BooleanField()
    token = models.CharField(
        max_length=255, verbose_name=_("Token"), default=generate_token
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    @property
    def unsubscribe_url(self):
        from django.urls import reverse

        return reverse(
            "public:unsubscribe",
            kwargs={
                "token": self.token,
            },
        )

    @property
    def confirm_url(self):
        from django.urls import reverse

        return reverse(
            "public:subscribe.confirm",
            kwargs={
                "token": self.token,
            },
        )

    class Meta:
        verbose_name = _("Subscriber")
        verbose_name_plural = _("Subscribers")
