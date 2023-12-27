import uuid

from django.core.management import BaseCommand
from django.test import Client

from monostat.opsgenie.models import OpsgenieConfiguration


class Command(BaseCommand):
    help = "Simulate alert hook from OpsGenie"

    def handle(self, *args, **options):
        secret = OpsgenieConfiguration.get_solo().secret
        alert_id = str(uuid.uuid4())
        client = Client()
        client.post(
            f"/integrations/opsgenie/hook/{secret}",
            data={
                # https://support.atlassian.com/opsgenie/docs/opsgenie-edge-connector-alert-action-data/
                "source": {"name": "web", "type": "API"},
                "alert": {
                    "updatedAt": 1420452193166002000,
                    "tags": ["tag1", "tag2"],
                    "teams": ["team1", "team2"],
                    "recipients": ["recipient1", "recipient2"],
                    "message": " test alert",
                    "username": "fili@ifountain.com",
                    "alertId": alert_id,
                    "source": "fili@ifountain.com",
                    "alias": "aliastest",
                    "tinyId": "23",
                    "createdAt": 1420452191104,
                    "userId": "daed1180-0ce8-438b-8f8e-57e1a5920a2d",
                    "entity": "",
                },
                "action": "Create",
                "integrationId": "37c8f316-17c6-49d7-899b-9c7e540c048d",
                "integrationName": "Integration1",
            },
            content_type="application/json",
        )

        print("Create sent. Press return to close alert.")
        input()

        client.post(
            f"/integrations/opsgenie/hook/{secret}",
            data={
                "source": {"name": "", "type": "web"},
                "alert": {
                    "updatedAt": 1420452374669001603,
                    "tags": ["tag1", "tag2"],
                    "message": "test alert",
                    "username": "fili@ifountain.com",
                    "alertId": alert_id,
                    "source": "fili@ifountain.com",
                    "alias": "aliastest",
                    "tinyId": "23",
                    "createdAt": 1420452191104,
                    "userId": "daed1180-0ce8-438b-8f8e-57e1a5920a2d",
                    "entity": "",
                },
                "action": "Close",
                "integrationId": "37c8f316-17c6-49d7-899b-9c7e540c048d",
                "integrationName": "Integration1",
            },
            content_type="application/json",
        )

        print("Close sent.")
