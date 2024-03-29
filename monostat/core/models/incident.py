from datetime import timezone

from django.db import models
from django.utils.translation import gettext_lazy as _


class Incident(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", _("planned")
        SUSPECTED = "suspected", _("suspected")
        DISMISSED = "dismissed", _("dismissed")
        CONFIRMED = "confirmed", _("confirmed")
        WATCHING = "watching", _("watching")
        RESOLVED = "resolved", _("resolved")

    class Severity(models.TextChoices):
        MAINTENANCE = "maintenance", _("Maintenance")
        NOTICE = "notice", _("Notice")
        BUG = "bug", _("Known Bug")
        PARTIAL = "partial", _("Partial Outage")
        OUTAGE = "outage", _("Outage")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=50,
        choices=Status,
    )
    severity = models.CharField(
        max_length=50,
        choices=Severity,
    )
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    title = models.TextField()
    summary = models.TextField(null=True, blank=True)
    slack_message_ts = models.CharField(max_length=100, null=True, blank=True)
    silent = models.BooleanField(
        default=False, verbose_name=_("Never send notifications for this incident")
    )
    last_notified_status = models.CharField(
        max_length=50,
        choices=Status,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Incident")
        verbose_name_plural = _("Incidents")
        ordering = ("-start", "-pk")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse(
            "public:detail",
            kwargs={
                "date": self.start.astimezone(timezone.utc).date().isoformat(),
                "pk": self.pk,
            },
        )


class IncidentUpdate(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    incident = models.ForeignKey(
        Incident, on_delete=models.CASCADE, related_name="updates"
    )
    new_status = models.CharField(
        choices=Incident.Status,
        max_length=50,
        null=True,
        blank=True,
    )
    message = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _("Incident update")
        verbose_name_plural = _("Incident updates")
        ordering = ("-created", "-pk")


class IncomingAlert(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    incident = models.ForeignKey(
        Incident, on_delete=models.CASCADE, related_name="incoming_alerts"
    )
    resolved = models.DateTimeField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    external_id = models.CharField(max_length=190, db_index=True)

    class Meta:
        verbose_name = _("Incoming alert")
        verbose_name_plural = _("Incoming alerts")
        ordering = ("-created", "-pk")
