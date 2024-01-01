from django.contrib.admin.models import CHANGE
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.timezone import now

from monostat.core.models import Incident
from monostat.core.utils.log import log
from monostat.slack.blocks import incident_message, incident_update_modal
from monostat.slack.models import SlackConfiguration
from monostat.slack.slack_app import app
from django.utils.translation import gettext as _


@app.action("dismiss_incident")
def on_dismiss_incident(ack, payload, body, client):
    user = body["user"]["username"]
    slack_conf = SlackConfiguration.get_solo()
    log_user = User.objects.get_or_create(
        username="_slack", defaults=dict(is_active=False)
    )[0]
    ack()
    with transaction.atomic():
        incident = Incident.objects.select_for_update().get(pk=payload["value"])
        incident.status = Incident.Status.DISMISSED
        incident.save(update_fields=["status"])
        log(
            log_user,
            obj=incident,
            message=_('Dismissed through slack by user "{user}"').format(
                user=user,
            ),
            action_flag=CHANGE,
        )
    client.chat_update(
        channel=slack_conf.channel_id,
        ts=incident.slack_message_ts,
        **incident_message(incident),
    )
    client.chat_postMessage(
        channel=slack_conf.channel_id,
        thread_ts=incident.slack_message_ts,
        text=_(
            'This incident has been dismissed on user request by user "{user}".'
        ).format(user=user),
    )


@app.action("link")
def on_link_clicked(ack):
    ack()


@app.action("confirm_incident")
def on_confirm_incident(ack, payload, body, client):
    user = body["user"]["username"]
    slack_conf = SlackConfiguration.get_solo()
    log_user = User.objects.get_or_create(
        username="_slack", defaults=dict(is_active=False)
    )[0]
    ack()
    with transaction.atomic():
        incident = Incident.objects.select_for_update().get(pk=payload["value"])
        incident.status = Incident.Status.CONFIRMED
        incident.save(update_fields=["status"])
        log(
            log_user,
            obj=incident,
            message=_('Confirmed through slack by user "{user}"').format(
                user=user,
            ),
            action_flag=CHANGE,
        )
        incident.updates.create(
            message=_(
                "Our team has confirmed that an incident is currently impacting "
                "our system. We are now looking into solutions and will update "
                "this page as soon has we have relevant information to share."
            ),
            new_status=Incident.Status.CONFIRMED,
        )
    client.chat_update(
        channel=slack_conf.channel_id,
        ts=incident.slack_message_ts,
        **incident_message(incident),
    )
    client.chat_postMessage(
        channel=slack_conf.channel_id,
        thread_ts=incident.slack_message_ts,
        text=_(
            'This incident has been confirmed on user request by user "{user}".'
        ).format(user=user),
    )


@app.action("update_incident")
def on_update_incident(ack, body, payload, client):
    incident = Incident.objects.get(pk=payload["value"])
    ack()
    client.views_open(
        trigger_id=body["trigger_id"], view=incident_update_modal(incident)
    )


@app.view("update_incident_modal")
def on_update_incident_modal(ack, body, client, view, logger):
    slack_conf = SlackConfiguration.get_solo()
    log_user = User.objects.get_or_create(
        username="_slack", defaults=dict(is_active=False)
    )[0]
    user = body["user"]["username"]
    ack()
    new_status = view["state"]["values"]["new_status"]["new_status"]["selected_option"]
    new_severity = view["state"]["values"]["new_severity"]["new_severity"][
        "selected_option"
    ]
    update_text = view["state"]["values"]["update_text"]["update_text"]["value"]
    updated_summary = view["state"]["values"]["new_summary"]["new_summary"]["value"]
    status_changed = False

    with transaction.atomic():
        incident = Incident.objects.select_for_update().get(pk=view["private_metadata"])
        if new_status and new_status["value"] != incident.status:
            status_changed = True
            incident.status = new_status["value"]
            incident.save(update_fields=["status"])
            if new_status["value"] == "resolved" and not incident.end:
                incident.end = now()
                incident.save(update_fields=["end"])
            log(
                log_user,
                obj=incident,
                message=_(
                    'Status changed to "{status}" through Slack by user "{user}"'
                ).format(
                    user=user,
                    status=new_status["value"],
                ),
                action_flag=CHANGE,
            )
            client.chat_postMessage(
                channel=slack_conf.channel_id,
                thread_ts=incident.slack_message_ts,
                text=_(
                    'This incident status has been updated to "{status}" on user request by user "{user}".'
                ).format(user=user, status=incident.get_status_display()),
            )

        if new_severity and new_severity["value"] != incident.severity:
            incident.severity = new_severity["value"]
            incident.save(update_fields=["severity"])
            log(
                log_user,
                obj=incident,
                message=_(
                    'Severity changed to "{severity}" through Slack by user "{user}"'
                ).format(
                    user=user,
                    severity=new_severity["value"],
                ),
                action_flag=CHANGE,
            )
            client.chat_postMessage(
                channel=slack_conf.channel_id,
                thread_ts=incident.slack_message_ts,
                text=_(
                    'This incident severity has been updated to "{severity}" on user request by user "{user}".'
                ).format(user=user, severity=incident.get_severity_display()),
            )

        if updated_summary and updated_summary != incident.summary:
            incident.summary = updated_summary
            incident.save(update_fields=["summary"])
            log(
                log_user,
                obj=incident,
                message=_('Summary changed through Slack by user "{user}"').format(
                    user=user,
                ),
                action_flag=CHANGE,
            )
            client.chat_postMessage(
                channel=slack_conf.channel_id,
                thread_ts=incident.slack_message_ts,
                text=_(
                    'This incident summary has on user request by user "{user}".'
                ).format(user=user, severity=incident.get_severity_display()),
            )

        if update_text:
            incident.updates.create(
                message=update_text,
                new_status=(
                    incident.status
                    if status_changed
                    or not incident.updates.filter(new_status=incident.status).exists()
                    else None
                ),
            )
            log(
                log_user,
                obj=incident,
                message=_('Update added through Slack by user "{user}"').format(
                    user=user,
                ),
                action_flag=CHANGE,
            )
            client.chat_postMessage(
                channel=slack_conf.channel_id,
                thread_ts=incident.slack_message_ts,
                text=_(
                    'An incident update has been added on user request by user "{user}":'
                ).format(user=user, severity=incident.get_severity_display()),
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": _(
                                'An incident update has been added on user request by user "{user}":'
                            ).format(
                                user=user, severity=incident.get_severity_display()
                            ),
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "\n".join(
                                f"> {l}" for l in update_text.splitlines()
                            ),
                        },
                    },
                ],
            )

    client.chat_update(
        channel=slack_conf.channel_id,
        ts=incident.slack_message_ts,
        **incident_message(incident),
    )
