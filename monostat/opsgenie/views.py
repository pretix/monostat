import json

from django.contrib.admin.models import ADDITION, CHANGE
from django.contrib.auth.models import User
from django.core.exceptions import BadRequest, PermissionDenied
from django.db import transaction
from django.http import HttpResponse
from django.utils.crypto import constant_time_compare
from django.utils.timezone import now
from django.utils.translation import gettext
from django.views.decorators.csrf import csrf_exempt

from monostat.core.models import IncomingAlert, Incident
from monostat.core.utils.log import log
from monostat.opsgenie.models import OpsgenieConfiguration


@csrf_exempt
@transaction.atomic()
def webhook(request, secret):
    config = OpsgenieConfiguration.get_solo()
    user = User.objects.get_or_create(
        username="_opsgenie", defaults=dict(is_active=False)
    )[0]
    if not constant_time_compare(secret, config.secret):
        raise PermissionDenied("Incorrect secret.")
    try:
        data = json.loads(request.body)
        action = data["action"]
        alert_id = data["alert"]["alertId"]
    except:
        raise BadRequest("Invalid JSON body")

    if action in ("Create", "UpdateMessage"):
        try:
            incident, incident_created = Incident.objects.get_or_create(
                status__in=(
                    Incident.Status.SUSPECTED,
                    Incident.Status.CONFIRMED,
                    Incident.Status.WATCHING,
                ),
                severity__in=(Incident.Severity.PARTIAL, Incident.Severity.OUTAGE),
                defaults={
                    "status": Incident.Status.SUSPECTED,
                    "severity": Incident.Severity.OUTAGE,
                    "start": now(),
                    "title": "Outage",
                },
            )
        except Incident.MultipleObjectsReturned:
            incident = Incident.objects.filter(
                status__in=(
                    Incident.Status.SUSPECTED,
                    Incident.Status.CONFIRMED,
                    Incident.Status.WATCHING,
                ),
                severity__in=(Incident.Severity.PARTIAL, Incident.Severity.OUTAGE),
            ).first()
            incident_created = False
        alert, alert_created = IncomingAlert.objects.update_or_create(
            external_id=alert_id,
            defaults={
                "message": data["alert"].get("message", ""),
                "incident": incident,
            },
        )
        if incident_created:
            log(
                user,
                obj=incident,
                message="Incident created through OpsGenie",
                action_flag=ADDITION,
            )
            incident.updates.create(
                message=gettext(
                    "Our automated monitoring system has detected an outage. Our team has "
                    "been alerted and is looking into the issue. We will update this page "
                    "if we have relevant information to share."
                )
            )
            # todo: send message to slack asking to confirm
        if alert_created:
            log(
                user,
                obj=incident,
                message=f"New alert {alert_id} created through OpsGenie",
                action_flag=ADDITION,
            )
    elif action == "Close":
        for alert in IncomingAlert.objects.filter(
            external_id=alert_id, resolved__isnull=True
        ):
            alert.resolved = now()
            alert.save()
            incident = alert.incident
            log(
                user,
                obj=incident,
                message=f"Alerts {alert_id} closed through OpsGenie",
                action_flag=CHANGE,
            )
            if not incident.incoming_alerts.filter(resolved__isnull=True).exists():
                if incident.status == Incident.Status.SUSPECTED:
                    incident.status = Incident.Status.DISMISSED
                    incident.end = now()
                    incident.save(update_fields=["status", "end"])
                    log(
                        user,
                        obj=incident,
                        message=f"Incident dismissed through OpsGenie",
                        action_flag=CHANGE,
                    )
                    # todo: send message to slack inviting to resolve history
                else:
                    log(
                        user,
                        obj=incident,
                        message=f"All alerts closed  OpsGenie",
                        action_flag=CHANGE,
                    )
                    # todo: send message to slack proposing to resolve the incident
    return HttpResponse("OK")
