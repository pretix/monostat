from django.db import models
from solo.models import SingletonModel
from django.utils.translation import gettext_lazy as _


class SiteConfiguration(SingletonModel):
    system_name = models.CharField(
        max_length=255, verbose_name=_("System name"), default="pretix"
    )
    support_email = models.EmailField(
        verbose_name=_("Support email"), default="support@pretix.eu"
    )
    support_phone = models.CharField(
        verbose_name=_("Support phone"), default="+49 6221 3217750", max_length=50
    )
    legal_url = models.URLField(
        verbose_name=_("Legal notice URL"), default="https://pretix.eu/about/en/imprint"
    )
    privacy_url = models.URLField(
        verbose_name=_("Privacy policy URL"),
        default="https://pretix.eu/about/en/privacy",
    )
    primary_color = models.CharField(
        verbose_name=_("Primary color"), default="#3B1C4A", max_length=50
    )
    link_color = models.CharField(
        verbose_name=_("Link color"), default="#7F4A91", max_length=50
    )
    success_color = models.CharField(
        verbose_name=_("Success color"), default="#50A167", max_length=50
    )
    warning_color = models.CharField(
        verbose_name=_("Warning color"), default="#FFB419", max_length=50
    )
    danger_color = models.CharField(
        verbose_name=_("Danger color"), default="#C44F4F", max_length=50
    )
    info_color = models.CharField(
        verbose_name=_("Info color"), default="#5F9CD4", max_length=50
    )
    primary_text_color = models.CharField(
        verbose_name=_("Primary text color"), default="#333333", max_length=50
    )
    secondary_text_color = models.CharField(
        verbose_name=_("Secondary text color"), default="#767676", max_length=50
    )
    logo = models.FileField(
        verbose_name=_("Logo"),
        null=True,
        blank=True,
    )

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = _("Site Configuration")
