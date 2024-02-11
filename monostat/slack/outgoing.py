from urllib.parse import urljoin

from django.conf import settings
from django.contrib.admin.models import CHANGE
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from huey.contrib.djhuey import db_task

from monostat.core.models import Incident
from monostat.core.utils.admin import url_to_edit_object
from monostat.core.utils.log import log
from monostat.slack.blocks import incident_message
from monostat.slack.models import SlackConfiguration
from monostat.slack.slack_app import app


@db_task(priority=50, retries=5)
def on_new_incident_created_by_alert(incident, alert_message):
    user = User.objects.get_or_create(
        username="_slack", defaults=dict(is_active=False)
    )[0]
    slack_conf = SlackConfiguration.get_solo()
    app.client.token = slack_conf.bot_token
    m = app.client.chat_postMessage(
        channel=slack_conf.channel_id, **incident_message(incident, alert_message)
    )
    incident.slack_message_ts = m["ts"]
    incident.save(update_fields=["slack_message_ts"])

    log(
        user,
        obj=incident,
        message="Sent notification to Slack",
        action_flag=CHANGE,
    )


@db_task()
def on_autoresolved_incident(incident):
    slack_conf = SlackConfiguration.get_solo()
    app.client.token = slack_conf.bot_token
    app.client.chat_update(
        channel=slack_conf.channel_id,
        ts=incident.slack_message_ts,
        **incident_message(incident),
    )
    text = _(
        "This incident has just been dismissed automatically through "
        "OpsGenie. Please take the time and review if it was an actual incident "
        "or a false alarm. If it was a real incident, please update the incident "
        "manually to fix the status page history!"
    )
    app.client.chat_postMessage(
        channel=slack_conf.channel_id,
        thread_ts=incident.slack_message_ts,
        reply_broadcast=True,
        text=text,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text,
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": _("View and change incident"),
                        "emoji": True,
                    },
                    "url": urljoin(settings.SITE_URL, url_to_edit_object(incident)),
                    "action_id": "link",
                },
            }
        ],
    )


@db_task(priority=20, retries=5)
def on_all_alerts_resolved_incident(incident):
    slack_conf = SlackConfiguration.get_solo()
    app.client.token = slack_conf.bot_token
    app.client.chat_update(
        channel=slack_conf.channel_id,
        ts=incident.slack_message_ts,
        **incident_message(incident),
    )
    app.client.chat_postMessage(
        channel=slack_conf.channel_id,
        thread_ts=incident.slack_message_ts,
        reply_broadcast=True,
        text=_(
            "All OpsGenie alerts have been closed for the incident. Remember to "
            'update this incident to "resolved" once it is fully over so the '
            "status page is up to date! New OpsGenie alerts will be ignored until "
            "this has been resolved."
        ),
    )


@db_task(priority=20, retries=5)
def on_changed_incident(incident_id, change_message=None):
    incident = Incident.objects.get(pk=incident_id)
    slack_conf = SlackConfiguration.get_solo()
    app.client.token = slack_conf.bot_token
    if incident.slack_message_ts:
        app.client.chat_update(
            channel=slack_conf.channel_id,
            ts=incident.slack_message_ts,
            **incident_message(incident),
        )
    else:
        m = app.client.chat_postMessage(
            channel=slack_conf.channel_id, **incident_message(incident)
        )
        incident.slack_message_ts = m["ts"]
        incident.save(update_fields=["slack_message_ts"])

    if change_message:
        app.client.chat_postMessage(
            channel=slack_conf.channel_id,
            thread_ts=incident.slack_message_ts,
            text=change_message,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": change_message,
                    },
                },
            ],
        )
