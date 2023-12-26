from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import User, Group
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
    list_display = ["title", "status", "severity", "start", "end"]
    list_filter = ["status", "severity", "start", "end"]


site = MonostatAdminSite(name="admin")
site.register(SiteConfiguration, SiteConfigurationAdmin)
site.register(Incident, IncidentAdmin)
site.register(User, UserAdmin)
site.register(Group, GroupAdmin)
