import calendar
import zoneinfo
from datetime import timezone, date, timedelta, datetime

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    TemplateView,
    DetailView,
    DeleteView,
    CreateView,
)

from monostat.core.models import Incident
from monostat.notifications.models import Subscriber, NotificationConfiguration
from monostat.notifications.tasks import send_optin
from monostat.public.context import contextprocessor


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
        recent_incidents = Incident.objects.filter(
            Q(end__gt=now() - timedelta(hours=24))
            | Q(start__gt=now() - timedelta(hours=24)),
            status=Incident.Status.RESOLVED,
        ).prefetch_related("updates")

        return super().get_context_data(
            planned_incidents=planned_incidents,
            current_incidents=current_incidents,
            recent_incidents=recent_incidents,
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
                        tzinfo=tz,
                    )
                    if d_start > now():
                        newweek.append((0, None, set()))
                        continue
                    d_end = datetime(
                        *year_month,
                        day,
                        hour=23,
                        minute=59,
                        second=59,
                        microsecond=999999,
                        tzinfo=tz,
                    )
                    severities = {
                        i.severity
                        for i in incidents
                        if (
                            d_start <= i.start <= d_end
                            or (i.end and d_start <= i.end <= d_end)
                            or (i.end and d_start >= i.start and d_end <= i.end)
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
                year_month = year_month[0] + 1, 1

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
            status__in=(
                Incident.Status.SUSPECTED,
                Incident.Status.CONFIRMED,
                Incident.Status.WATCHING,
                Incident.Status.PLANNED,
                Incident.Status.RESOLVED,
            ),
        ).prefetch_related("updates")

        return super().get_context_data(
            day=d,
            incidents=incidents,
        )


@method_decorator(csrf_exempt, name="dispatch")
class UnsubscribeView(DeleteView):
    model = Subscriber
    slug_url_kwarg = "token"
    slug_field = "token"
    template_name = "public/unsubscribe.html"

    def get_success_url(self):
        return reverse("public:unsubscribe.done")

    def form_valid(self, form):
        r = super().form_valid(form)
        if "csrfmiddlewaretoken" not in self.request.POST:
            # One-click unsubscribe as per https://datatracker.ietf.org/doc/html/rfc8058
            # does not allow redirects
            return render(self.request, "public/unsubscribe_done.html")
        return r


class UnsubscribeDoneView(TemplateView):
    template_name = "public/unsubscribe_done.html"


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ["email"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if Subscriber.objects.filter(email__iexact=email, active=True).exists():
            raise ValidationError(_("You are already subscribed."))
        if Subscriber.objects.filter(
            email__iexact=email, active=False, created__gt=now() - timedelta(hours=24)
        ).exists():
            raise ValidationError(
                _("You have already tried subscribing in the last 24 hours.")
            )
        return email


class SubscribeView(CreateView):
    model = Subscriber
    template_name = "public/subscribe.html"
    form_class = SubscribeForm

    def dispatch(self, request, *args, **kwargs):
        nc = NotificationConfiguration.get_solo()
        if not nc.allow_subscriptions:
            raise PermissionDenied("Feature disabled")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("public:subscribe.done")

    def form_valid(self, form):
        Subscriber.objects.filter(
            email__iexact=form.cleaned_data["email"], active=False
        ).delete()
        form.instance.active = False
        form.instance.save()
        transaction.on_commit(lambda: send_optin(form.instance.pk))
        return redirect(self.get_success_url())


class SubscribeConfirmView(DeleteView):
    model = Subscriber
    slug_url_kwarg = "token"
    slug_field = "token"
    template_name = "public/subscribe_confirm.html"

    def form_valid(self, form):
        self.object.active = True
        self.object.save()
        Subscriber.objects.filter(email__iexact=self.object.email).exclude(
            pk=self.object.pk
        ).delete()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse("public:subscribe.confirmed")


class SubscribeDoneView(TemplateView):
    template_name = "public/subscribe_done.html"


class SubscribeConfirmedView(TemplateView):
    template_name = "public/subscribe_confirmed.html"


def handler404(request, *args, **kwargs):
    return render(request, "public/404.html")


def handler500(request, *args, **kwargs):
    ctx = {}
    try:
        ctx.update(contextprocessor(request))
    except:
        pass
    return render(None, "public/500.html", ctx)
