# Generated by Django 5.0 on 2024-01-01 20:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="incident",
            options={
                "ordering": ("-start", "-pk"),
                "verbose_name": "Incident",
                "verbose_name_plural": "Incidents",
            },
        ),
        migrations.AlterModelOptions(
            name="incidentupdate",
            options={
                "ordering": ("-created", "-pk"),
                "verbose_name": "Incident update",
                "verbose_name_plural": "Incident updates",
            },
        ),
        migrations.AlterModelOptions(
            name="incomingalert",
            options={
                "ordering": ("-created", "-pk"),
                "verbose_name": "Incoming alert",
                "verbose_name_plural": "Incoming alerts",
            },
        ),
        migrations.AddField(
            model_name="incident",
            name="slack_message_ts",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="incidentupdate",
            name="incident",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="updates",
                to="core.incident",
            ),
        ),
        migrations.AlterField(
            model_name="incomingalert",
            name="incident",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="incoming_alerts",
                to="core.incident",
            ),
        ),
    ]
