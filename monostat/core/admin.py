from django import forms
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from multifactor.admin import MultifactorUserAdmin
from solo.admin import SingletonModelAdmin

from .models import Incident, IncidentUpdate, IncomingAlert, SiteConfiguration
from ..notifications.tasks import send_notifications
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


class IncidentForm(forms.ModelForm):
    skip_notify = forms.BooleanField(
        label="Do not notify subscribers (this change only)", required=False
    )

    class Meta:
        models = Incident


class IncidentAdmin(admin.ModelAdmin):
    inlines = [IncidentUpdateInline, IncomingAlertInline]
    list_display = ["title", "status", "severity", "start", "end"]
    list_filter = ["status", "severity", "start", "end"]
    readonly_fields = ["created", "updated", "slack_message_ts", "last_notified_status"]
    form = IncidentForm

    def save_model(self, request, obj, form, change):
        r = super().save_model(request, obj, form, change)
        text = (
            f'The incident has been updated on the admin page by user "{request.user}".'
        )
        transaction.on_commit(lambda: on_changed_incident(obj.pk, text))
        if not form.cleaned_data.get("skip_notify"):
            transaction.on_commit(lambda: send_notifications(obj.pk))
        return r


class CustomUserAdmin(UserAdmin, MultifactorUserAdmin):
    pass


site = MonostatAdminSite(name="admin")
site.register(SiteConfiguration, SiteConfigurationAdmin)
site.register(Incident, IncidentAdmin)
site.register(User, CustomUserAdmin)
site.register(Group, GroupAdmin)
