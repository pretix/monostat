from django.conf import settings
from django.template.loader import get_template

from monostat.core.models import SiteConfiguration
from monostat.notifications.models import NotificationConfiguration


def contextprocessor(request):
    tz = settings.TIME_ZONE
    config = SiteConfiguration.get_solo()
    notification_config = NotificationConfiguration.get_solo()

    theme_template = get_template("public/theme.css.tpl")
    theme_css = theme_template.render(
        {
            "config": config,
        }
    )

    return {
        "config": config,
        "theme_css": theme_css,
        "notification_config": notification_config,
        "tz": tz,
    }
