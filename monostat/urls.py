from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from monostat.core.admin import site
from monostat.opsgenie import urls as opsgenie_urls
from monostat.public import urls as public_urls
from monostat.slack import urls as slack_urls

urlpatterns = (
    [
        path("admin/", site.urls),
        path("", include((public_urls, "public"))),
        path("integrations/opsgenie/", include((opsgenie_urls, "opsgenie"))),
        path("integrations/slack/", include((slack_urls, "slack"))),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)

handler404 = "monostat.public.views.handler404"
handler500 = "monostat.public.views.handler500"
