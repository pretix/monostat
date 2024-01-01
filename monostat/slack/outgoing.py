from django.utils.translation import gettext as _

from monostat.slack.models import SlackConfiguration
from monostat.slack.slack_app import app


def on_new_incident_created_by_alert(incident, alert_message):
    slack_conf = SlackConfiguration.get_solo()
    text = _(
        "*OpsGenie has reported a new incident.* The status page now shows "
        "a suspected downtime. Please check if this is really an incident "
        "that causes a user-visible issue on production. If yes, please "
        "confirm the incident."
    )
    app.client.token = slack_conf.bot_token
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
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": _("Alert message: {msg}").format(msg=alert_message),
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": _(":fire: Yes, this is a real incident"),
                            "emoji": True,
                        },
                        "style": "primary",
                        "value": f"{incident.pk}",
                        "action_id": "confirm_incident",
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": _("Dismiss incident"),
                            "emoji": True,
                        },
                        "value": f"{incident.pk}",
                        "action_id": "dismiss_incident",
                        "style": "danger",
                        "confirm": {
                            "title": {"type": "plain_text", "text": _("Are you sure?")},
                            "text": {
                                "type": "plain_text",
                                "text": _(
                                    "This will hide the incident from the status page."
                                ),
                            },
                            "confirm": {
                                "type": "plain_text",
                                "text": _("Dismiss incident"),
                            },
                            "deny": {"type": "plain_text", "text": _("Cancel")},
                        },
                    },
                ],
            },
        ],
    )
