from solo.admin import SingletonModelAdmin

from .models import OpsgenieConfiguration
from ..core.admin import site


class OpsgenieConfigurationAdmin(SingletonModelAdmin):
    pass


site.register(OpsgenieConfiguration, OpsgenieConfigurationAdmin)
