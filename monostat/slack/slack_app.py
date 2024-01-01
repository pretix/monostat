import logging

from slack_bolt import App
from slack_bolt.authorization import AuthorizeResult
from slack_bolt.middleware import RequestVerification

from monostat.slack.models import SlackConfiguration

logger = logging.getLogger(__name__)


def authorize(enterprise_id, team_id, logger):
    conf = SlackConfiguration.get_solo()

    for m in app._middleware_list:
        if isinstance(m, RequestVerification):
            m.verifier.signing_secret = conf.signing_secret

    return AuthorizeResult(
        enterprise_id=enterprise_id,
        team_id=team_id,
        bot_token=conf.bot_token,
    )


app = App(
    authorize=authorize,
    signing_secret="will-be-replaced-later",
)
try:
    authorize(None, None, None)
finally:
    logger.exception("Could not set signing token")