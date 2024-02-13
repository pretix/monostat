import logging
from urllib.parse import urljoin

import css_inline
from django.conf import settings
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.translation import gettext as _
from huey.contrib.djhuey import db_task, lock_task

from monostat.core.models import SiteConfiguration, Incident
from monostat.notifications.models import Subscriber

logger = logging.getLogger(__name__)


@db_task(priority=0)
@lock_task("send-notifications")
def send_notifications(incident_id):
    incident = Incident.objects.get(pk=incident_id)

    if incident.silent:
        return

    if incident.status not in (
        Incident.Status.CONFIRMED,
        Incident.Status.WATCHING,
        Incident.Status.RESOLVED,
    ):
        # Do not notify about suspected, dismissed or planned incidents
        return

    if incident.status == incident.last_notified_status:
        # Already notified about this status
        return

    conf = SiteConfiguration.get_solo()
    incident_is_new = (
        incident.last_notified_status is None
        and incident.status == Incident.Status.CONFIRMED
    )
    if incident_is_new:
        plain_subject = _("New incident confirmed")
        subject = f"[{incident.get_severity_display()}] {plain_subject}"
    else:
        plain_subject = _("Incident updated")
        subject = f"[{incident.get_severity_display()}] [{incident.get_status_display()}] {plain_subject}"
    ctx = {
        "incident": incident,
        "incident_url": urljoin(settings.SITE_URL, incident.get_absolute_url()),
        "incident_is_new": incident_is_new,
        "conf": conf,
        "settings": settings,
        "subject": plain_subject,
    }

    with mail.get_connection() as connection:
        for subscriber in Subscriber.objects.filter(active=True):
            ctx["unsubscribe_url"] = urljoin(
                settings.SITE_URL, subscriber.unsubscribe_url
            )

            tpl_html = get_template("notifications/notification.html")
            body_html = tpl_html.render(ctx)
            inliner = css_inline.CSSInliner()
            body_html = inliner.inline(body_html)

            tpl_plain = get_template("notifications/notification.txt")
            body_plain = tpl_plain.render(ctx)

            from_name = _("%(system)s System Status") % {"system": conf.system_name}

            msg = EmailMultiAlternatives(
                subject,
                body_plain,
                f"{from_name} <{settings.MAIL_FROM}>",
                [subscriber.email],
                connection=connection,
                headers={
                    "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
                    "List-Unsubscribe": f"<{ctx['unsubscribe_url']}>",
                },
            )
            msg.attach_alternative(body_html, "text/html")
            try:
                msg.send()
            except:
                logger.exception("Could not send mail.")

    incident.last_notified_status = incident.status
    incident.save(update_fields=["last_notified_status"])


@db_task(priority=0)
def send_optin(subscriber_id):
    subscriber = Subscriber.objects.get(pk=subscriber_id)
    conf = SiteConfiguration.get_solo()

    if subscriber.active:
        return

    subject = _("Confirm subscription")
    ctx = {
        "conf": conf,
        "settings": settings,
        "subject": subject,
        "confirm_url": urljoin(settings.SITE_URL, subscriber.confirm_url),
    }

    tpl_html = get_template("notifications/confirm.html")
    body_html = tpl_html.render(ctx)
    inliner = css_inline.CSSInliner()
    body_html = inliner.inline(body_html)

    tpl_plain = get_template("notifications/confirm.txt")
    body_plain = tpl_plain.render(ctx)

    from_name = _("%(system)s System Status") % {"system": conf.system_name}

    msg = EmailMultiAlternatives(
        subject,
        body_plain,
        f"{from_name} <{settings.MAIL_FROM}>",
        [subscriber.email],
    )
    msg.attach_alternative(body_html, "text/html")
    try:
        msg.send()
    except:
        logger.exception("Could not send mail.")
