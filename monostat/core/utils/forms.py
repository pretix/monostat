from django import forms
from django.urls import reverse

SECRET_REDACTED = "*****"


class SecretKeyWidget(forms.TextInput):
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update(
            {
                "autocomplete": "new-password"  # see https://bugs.chromium.org/p/chromium/issues/detail?id=370363#c7
            }
        )
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        if value:
            value = SECRET_REDACTED
        return super().get_context(name, value, attrs)


class SecretKeyField(forms.CharField):
    widget = SecretKeyWidget

    def has_changed(self, initial, data):
        if data == SECRET_REDACTED:
            return False
        return super().has_changed(initial, data)

    def run_validators(self, value):
        if value == SECRET_REDACTED:
            return
        return super().run_validators(value)


class SecretKeyFormMixin:
    def clean(self):
        d = self.cleaned_data
        for k, v in self.cleaned_data.items():
            if (
                isinstance(self.fields.get(k), SecretKeyField)
                and d.get(k) == SECRET_REDACTED
            ):
                d[k] = self.initial[k]
        return d
