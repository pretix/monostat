from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from solo.admin import SingletonModelAdmin

from .models import Incident, IncidentUpdate, IncomingAlert, SiteConfiguration
from ..slack.outgoing import on_changed_incident


class MonostatAdminSite(admin.AdminSite):
    site_header = _("Status page admin")
    site_title = _("Status page admin")


class SiteConfigurationAdmin(SingletonModelAdmin):
    pass


class IncidentUpdateInline(admin.StackedInline):
    model = IncidentUpdate
    readonly_fields = ["created"]
    extra = 0


class IncomingAlertInline(admin.StackedInline):
    model = IncomingAlert
    extra = 0


class IncidentAdmin(admin.ModelAdmin):
    inlines = [IncidentUpdateInline, IncomingAlertInline]
    list_display = ["title", "status", "severity", "start", "end"]
    list_filter = ["status", "severity", "start", "end"]
    readonly_fields = ["created", "updated", "slack_message_ts"]

    def save_model(self, request, obj, form, change):
        r = super().save_model(request, obj, form, change)
        text = (
            f'The incident has been updated on the admin page by user "{request.user}".'
        )
        transaction.on_commit(lambda: on_changed_incident(obj, text))
        return r


site = MonostatAdminSite(name="admin")
site.register(SiteConfiguration, SiteConfigurationAdmin)
site.register(Incident, IncidentAdmin)
site.register(User, UserAdmin)
site.register(Group, GroupAdmin)
