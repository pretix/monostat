from django.contrib.admin import ModelAdmin
from solo.admin import SingletonModelAdmin

from .models import NotificationConfiguration, Subscriber
from ..core.admin import site


class NotificationConfigurationAdmin(SingletonModelAdmin):
    pass


class SubscriberAdmin(ModelAdmin):
    list_display = ["email", "active"]
    readonly_fields = ["token"]


site.register(NotificationConfiguration, NotificationConfigurationAdmin)
site.register(Subscriber, SubscriberAdmin)
