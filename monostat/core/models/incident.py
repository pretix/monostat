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
        OUTAGE = "outage", _("Full Outage")

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

    class Meta:
        verbose_name = _("Incident")
        verbose_name_plural = _("Incidents")


class IncidentUpdate(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
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


class IncomingAlert(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    resolved = models.DateTimeField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    external_id = models.CharField(max_length=190, db_index=True)

    class Meta:
        verbose_name = _("Incoming alert")
        verbose_name_plural = _("Incoming alerts")
