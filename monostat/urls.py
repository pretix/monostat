from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from monostat.core.admin import site

urlpatterns = (
    [
        path("admin/", site.urls),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
