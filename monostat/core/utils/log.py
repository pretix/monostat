from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType


def log(user, obj, message, action_flag=CHANGE):
    LogEntry.objects.create(
        user=user,
        content_type=ContentType.objects.get_for_model(type(obj)),
        object_id=obj.pk,
        object_repr=str(obj),
        action_flag=action_flag,
        change_message=message,
    )
