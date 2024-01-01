from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from slack_bolt.util.utils import create_web_client
from slack_sdk.errors import SlackApiError
from solo.admin import SingletonModelAdmin

from .models import SlackConfiguration
from ..core.admin import site
from ..core.utils.forms import SecretKeyFormMixin, SecretKeyField, SECRET_REDACTED


class SlackConfigurationForm(SecretKeyFormMixin, forms.ModelForm):
    bot_token = SecretKeyField()
    signing_secret = SecretKeyField()

    class Meta:
        model = SlackConfiguration
        exclude = []

    def _find_channel_id(self, bot_token, channel_name):
        try:
            client = create_web_client(
                # NOTE: the token here can be None
                token=bot_token,
            )
            r = client.conversations_list()
            for c in r["channels"]:
                if c.get("is_channel") and c.get("name") == channel_name:
                    return c["id"]
            while r["response_metadata"].get("next_cursor"):
                r = client.conversations_list(cursor=r["response_metadata"].get("next_cursor"))
                for c in r["channels"]:
                    if c.get("is_channel") and c.get("name") == channel_name:
                        return c["id"]
        except SlackApiError as e:
            raise ValidationError(_("Slack API error: {error}").format(error=str(e)))
        raise ValidationError(_("Could not find channel {channel}").format(channel=channel_name))

    def clean(self):
        d = self.cleaned_data
        d["channel_id"] = self._find_channel_id(
            self.instance.bot_token if d["bot_token"] == SECRET_REDACTED else d["bot_token"],
            d["channel_name"].replace("#", "")
        )
        return d


class SlackConfigurationAdmin(SingletonModelAdmin):
    form = SlackConfigurationForm


site.register(SlackConfiguration, SlackConfigurationAdmin)
