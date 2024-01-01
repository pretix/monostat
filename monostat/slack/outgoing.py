from urllib.parse import urljoin

from django.conf import settings
from django.contrib.admin.models import CHANGE
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from monostat.core.utils.admin import url_to_edit_object
from monostat.core.utils.log import log
from monostat.slack.blocks import incident_message
from monostat.slack.models import SlackConfiguration
from monostat.slack.slack_app import app


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


def on_autoresolved_incident(incident):
    slack_conf = SlackConfiguration.get_solo()
    app.client.token = slack_conf.bot_token
    app.client.chat_update(
        channel=slack_conf.channel_id,
        ts=incident.slack_message_ts,
        **incident_message(incident)
    )
    app.client.chat_postMessage(
        channel=slack_conf.channel_id,
        thread_ts=incident.slack_message_ts,
        text=_("This incident has been dismissed automatically through OpsGenie."),
    )
    text = _(
        "An incident has just been created and dismissed automatically through "
        "OpsGenie. Please take the time and review if it was an actual incident "
        "or a false alarm. If it was a real incident, please update the status "
        "page history accordingly!"
    )
    app.client.chat_postMessage(
        channel=slack_conf.channel_id,
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
