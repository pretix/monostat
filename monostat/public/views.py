import calendar
import zoneinfo
from datetime import timezone, date, timedelta, datetime

from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.urls import reverse
from django.utils.timezone import now
from django.views.generic import TemplateView, DetailView

from monostat.core.models import Incident


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


class HistoryView(TemplateView):
    template_name = "public/history.html"

    def get_context_data(self, **kwargs):
        tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
        incidents = Incident.objects.filter(
            Q(start__gte=now() - timedelta(days=395))
            | Q(end__gte=now() - timedelta(days=395)),
            status__in=(
                Incident.Status.SUSPECTED,
                Incident.Status.CONFIRMED,
                Incident.Status.WATCHING,
                Incident.Status.PLANNED,
                Incident.Status.RESOLVED,
            ),
        )

        year_month = now().year - 1, now().month + 1
        if year_month[1] > 12:
            year_month = now().year, 1
        months = []
        for i in range(12):
            monthcal = []
            for week in calendar.monthcalendar(*year_month):
                newweek = []
                for day in week:
                    if day == 0:
                        newweek.append((day, None, set()))
                        continue
                    d_start = datetime(
                        *year_month,
                        day,
                        hour=0,
                        minute=0,
                        second=0,
                        microsecond=0,
                        tzinfo=tz
                    )
                    d_end = datetime(
                        *year_month,
                        day,
                        hour=23,
                        minute=59,
                        second=59,
                        microsecond=999999,
                        tzinfo=tz
                    )
                    severities = {
                        i.severity
                        for i in incidents
                        if (
                            d_start < i.start < d_end
                            or (i.end and d_end < i.end < d_end)
                            or (i.end and d_start > i.start and d_end < i.end)
                        )
                    }
                    newweek.append(
                        (
                            day,
                            reverse(
                                "public:day",
                                kwargs={"date": d_start.strftime("%Y-%m-%d")},
                            ),
                            severities,
                        )
                    )
                monthcal.append(newweek)
            months.append((date(*year_month, 1), monthcal))
            year_month = year_month[0], year_month[1] + 1
            if year_month[1] > 12:
                year_month = year_month[1] + 0, 1

        return super().get_context_data(
            months=reversed(months),
        )


class DayView(TemplateView):
    template_name = "public/day.html"

    def get_context_data(self, **kwargs):
        tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
        d = date.fromisoformat(self.kwargs.get("date"))
        d_start = datetime(
            d.year, d.month, d.day, hour=0, minute=0, second=0, microsecond=0, tzinfo=tz
        )
        d_end = datetime(
            d.year,
            d.month,
            d.day,
            hour=23,
            minute=59,
            second=59,
            microsecond=999999,
            tzinfo=tz,
        )
        incidents = Incident.objects.filter(
            Q(
                Q(start__gte=d_start, start__lte=d_end)
                | Q(end__gte=d_start, end__lte=d_end)
                | Q(end__gte=d_end, start__lte=d_start)
            ),
        ).prefetch_related("updates")

        return super().get_context_data(
            day=d,
            incidents=incidents,
        )
