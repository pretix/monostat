import zoneinfo
from urllib.parse import urljoin

from django.conf import settings
from django.utils.formats import date_format
from django.utils.translation import gettext as _

from monostat.core.models import Incident
from monostat.core.utils.admin import url_to_edit_object


def incident_message(incident, alert_message=None):
    tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
    if incident.status == Incident.Status.SUSPECTED:
        text = _(
            "*OpsGenie has reported a new incident.* The status page now shows "
            "a suspected downtime. Please check if this is really an incident "
            "that causes a user-visible issue on production. If yes, please "
            "confirm the incident."
        )
    elif incident.status == Incident.Status.RESOLVED:
        text = _("Resolved incident:")
    elif incident.status == Incident.Status.DISMISSED:
        text = _("Dismissed incident:")
    elif incident.status == Incident.Status.PLANNED:
        text = _("Planned maintenance (Start {start}):").format(
            start=date_format("SHORT_DATETIME_FORMAT", incident.start.astimezone(tz))
        )
    else:
        text = _("Ongoing incident:")

    m = dict(
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
                    "text": "*" + _("Incident title") + ":* " + incident.title,
                },
            },
        ],
    )

    if incident.status == Incident.Status.SUSPECTED:
        if alert_message:
            m["blocks"].append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": _("*Alert message:* {msg}").format(msg=alert_message),
                    },
                }
            )
        m["blocks"].append(
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
            }
        )
    elif incident.status == Incident.Status.DISMISSED:
        m["blocks"].append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": _(":no_bell: Incident dismissed."),
                },
            }
        )
    elif incident.status in (Incident.Status.CONFIRMED, Incident.Status.WATCHING):
        m["blocks"].append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": _(":fire: Incident confirmed and ongoing."),
                },
            }
        )
    elif incident.status == Incident.Status.RESOLVED:
        m["blocks"].append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": _(":white_check_mark: Incident resolved."),
                },
            }
        )

    if incident.status not in (Incident.Status.DISMISSED, Incident.Status.SUSPECTED):
        m["blocks"].append(
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": _("Update incident"),
                            "emoji": True,
                        },
                        "value": f"{incident.pk}",
                        "action_id": "update_incident",
                    },
                ],
            }
        )

    m["blocks"].append(
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "<%s|%s>"
                    % (
                        urljoin(settings.SITE_URL, url_to_edit_object(incident)),
                        _("Change on admin page"),
                    ),
                },
                {
                    "type": "mrkdwn",
                    "text": "<%s|%s>"
                    % (
                        urljoin(settings.SITE_URL, incident.get_absolute_url()),
                        _("View on public page"),
                    ),
                },
            ],
        }
    )
    return m


def incident_update_modal(incident: Incident):
    return {
        "type": "modal",
        "title": {"type": "plain_text", "text": _("Update incident"), "emoji": True},
        "callback_id": "update_incident_modal",
        "private_metadata": f"{incident.pk}",
        "submit": {"type": "plain_text", "text": _("Submit"), "emoji": True},
        "close": {"type": "plain_text", "text": _("Cancel"), "emoji": True},
        "blocks": [
            {
                "type": "input",
                "block_id": "new_status",
                "optional": True,
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": _("Keep current incident status ({status})").format(
                            status=incident.get_status_display()
                        ),
                        "emoji": True,
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": _("confirmed"),
                                "emoji": True,
                            },
                            "value": Incident.Status.CONFIRMED,
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": _("watching"),
                                "emoji": True,
                            },
                            "value": Incident.Status.WATCHING,
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": _("resolved"),
                                "emoji": True,
                            },
                            "value": Incident.Status.RESOLVED,
                        },
                    ],
                    "action_id": "new_status",
                },
                "label": {
                    "type": "plain_text",
                    "text": _("New incident status"),
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": _("If the status changes, subscribers will be notified."),
                },
            },
            {
                "type": "input",
                "block_id": "update_text",
                "optional": True,
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": _("Keep empty to not add a text update"),
                        "emoji": True,
                    },
                    "action_id": "update_text",
                },
                "label": {
                    "type": "plain_text",
                    "text": _("Update text"),
                    "emoji": True,
                },
            },
            {
                "type": "input",
                "block_id": "new_severity",
                "optional": True,
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": _("Keep current incident severity ({value})").format(
                            value=incident.get_severity_display()
                        ),
                        "emoji": True,
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": str(text),
                                "emoji": True,
                            },
                            "value": value,
                        }
                        for value, text in Incident.Severity.choices
                    ],
                    "action_id": "new_severity",
                },
                "label": {
                    "type": "plain_text",
                    "text": _("New incident severity"),
                    "emoji": True,
                },
            },
            {
                "type": "input",
                "block_id": "new_summary",
                "optional": True,
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "action_id": "new_summary",
                    "placeholder": {
                        "type": "plain_text",
                        "text": _("Keep empty to keep an empty summary"),
                        "emoji": True,
                    },
                    "initial_value": incident.summary or "",
                },
                "label": {
                    "type": "plain_text",
                    "text": _("Updated incident summary"),
                    "emoji": True,
                },
            },
        ],
    }


def home_view():
    return {
        "type": "home",
        "blocks": [
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": _("Create incident"),
                            "emoji": True,
                        },
                        "action_id": "create_incident",
                    }
                ],
            }
        ],
    }


def incident_create_modal():
    return {
        "type": "modal",
        "title": {"type": "plain_text", "text": _("Create incident"), "emoji": True},
        "callback_id": "create_incident_modal",
        "submit": {"type": "plain_text", "text": _("Submit"), "emoji": True},
        "close": {"type": "plain_text", "text": _("Cancel"), "emoji": True},
        "blocks": [
            {
                "type": "input",
                "block_id": "title",
                "element": {
                    "type": "plain_text_input",
                    "multiline": False,
                    "action_id": "title",
                    "placeholder": {
                        "type": "plain_text",
                        "text": _("Incident title"),
                        "emoji": True,
                    },
                },
                "label": {
                    "type": "plain_text",
                    "text": _("Incident title"),
                    "emoji": True,
                },
            },
            {
                "type": "input",
                "block_id": "status",
                "element": {
                    "type": "static_select",
                    "initial_option": {
                        "text": {
                            "type": "plain_text",
                            "text": _("confirmed"),
                            "emoji": True,
                        },
                        "value": Incident.Status.CONFIRMED,
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": _("planned"),
                                "emoji": True,
                            },
                            "value": Incident.Status.PLANNED,
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": _("confirmed"),
                                "emoji": True,
                            },
                            "value": Incident.Status.CONFIRMED,
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": _("watching"),
                                "emoji": True,
                            },
                            "value": Incident.Status.WATCHING,
                        },
                    ],
                    "action_id": "status",
                },
                "label": {
                    "type": "plain_text",
                    "text": _("Incident status"),
                    "emoji": True,
                },
            },
            {
                "type": "input",
                "block_id": "severity",
                "element": {
                    "type": "static_select",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": str(text),
                                "emoji": True,
                            },
                            "value": value,
                        }
                        for value, text in Incident.Severity.choices
                    ],
                    "action_id": "severity",
                },
                "label": {
                    "type": "plain_text",
                    "text": _("Severity"),
                    "emoji": True,
                },
            },
            {
                "type": "input",
                "block_id": "start",
                "optional": True,
                "element": {
                    "type": "datetimepicker",
                    "action_id": "start",
                },
                "label": {
                    "type": "plain_text",
                    "text": _("Incident start time"),
                    "emoji": True,
                },
            },
            {
                "type": "input",
                "block_id": "summary",
                "optional": True,
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "action_id": "summary",
                    "placeholder": {
                        "type": "plain_text",
                        "text": _("Incident summary"),
                        "emoji": True,
                    },
                },
                "label": {
                    "type": "plain_text",
                    "text": _("Incident summary"),
                    "emoji": True,
                },
            },
        ],
    }
