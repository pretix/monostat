from datetime import timezone

from django.http import Http404
from django.views.generic import TemplateView, DetailView

from monostat.core.models import SiteConfiguration, Incident


class ThemeCSSView(TemplateView):
    template_name = "public/theme.css.tpl"
    content_type = "text/css"

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            config=SiteConfiguration.get_solo(),
        )


class IndexView(TemplateView):
    template_name = "public/index.html"

    def get_context_data(self, **kwargs):
        planned_incidents = (
            Incident.objects.filter(
                status=Incident.Status.PLANNED,
            )
            .order_by("start", "pk")
            .prefetch_related("updates")
        )
        current_incidents = Incident.objects.filter(
            status__in=(
                Incident.Status.SUSPECTED,
                Incident.Status.CONFIRMED,
                Incident.Status.WATCHING,
            ),
        ).prefetch_related("updates")

        return super().get_context_data(
            config=SiteConfiguration.get_solo(),
            planned_incidents=planned_incidents,
            current_incidents=current_incidents,
            confirmed_severities={
                i.severity
                for i in current_incidents
                if i.status == Incident.Status.CONFIRMED
            },
            suspected_incidents=[
                i for i in current_incidents if i.status == Incident.Status.SUSPECTED
            ],
        )


class IncidentDetailView(DetailView):
    model = Incident
    pk_url_kwarg = "pk"
    queryset = Incident.objects.prefetch_related("updates")
    template_name = "public/incident_detail.html"
    context_object_name = "incident"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.start.astimezone(timezone.utc).date().isoformat() != self.kwargs.get(
            "date"
        ):
            raise Http404("Incident not found on this date")
        return obj

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            config=SiteConfiguration.get_solo(),
        )
