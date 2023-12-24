from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from solo.admin import SingletonModelAdmin

from .models import Incident, IncidentUpdate, IncomingAlert, SiteConfiguration


class MonostatAdminSite(admin.AdminSite):
    site_header = _("Status page admin")
    site_title = _("Status page admin")


class SiteConfigurationAdmin(SingletonModelAdmin):
    pass


class IncidentUpdateInline(admin.StackedInline):
    model = IncidentUpdate
    extra = 0


class IncomingAlertInline(admin.StackedInline):
    model = IncomingAlert
    extra = 0


class IncidentAdmin(admin.ModelAdmin):
    inlines = [IncidentUpdateInline, IncomingAlertInline]


site = MonostatAdminSite(name="admin")
site.register(SiteConfiguration, SiteConfigurationAdmin)
site.register(Incident, IncidentAdmin)
