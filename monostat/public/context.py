from django.conf import settings

from monostat.core.models import SiteConfiguration


def contextprocessor(request):
    tz = settings.TIME_ZONE
    return {
        "config": SiteConfiguration.get_solo(),
        "tz": tz,
    }
