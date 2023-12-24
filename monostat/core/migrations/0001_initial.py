# Generated by Django 5.0 on 2023-12-24 16:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Incident",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("planned", "planned"),
                            ("suspected", "suspected"),
                            ("dismissed", "dismissed"),
                            ("confirmed", "confirmed"),
                            ("watching", "watching"),
                            ("resolved", "resolved"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "severity",
                    models.CharField(
                        choices=[
                            ("maintenance", "Maintenance"),
                            ("notice", "Notice"),
                            ("bug", "Known Bug"),
                            ("partial", "Partial Outage"),
                            ("outage", "Full Outage"),
                        ],
                        max_length=50,
                    ),
                ),
                ("start", models.DateTimeField()),
                ("end", models.DateTimeField(blank=True, null=True)),
                ("title", models.TextField()),
                ("summary", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Incident",
                "verbose_name_plural": "Incidents",
            },
        ),
        migrations.CreateModel(
            name="IncidentUpdate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "new_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("planned", "planned"),
                            ("suspected", "suspected"),
                            ("dismissed", "dismissed"),
                            ("confirmed", "confirmed"),
                            ("watching", "watching"),
                            ("resolved", "resolved"),
                        ],
                        max_length=50,
                        null=True,
                    ),
                ),
                ("message", models.TextField(blank=True, null=True)),
                (
                    "incident",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.incident"
                    ),
                ),
            ],
            options={
                "verbose_name": "Incident update",
                "verbose_name_plural": "Incident updates",
            },
        ),
        migrations.CreateModel(
            name="IncomingAlert",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("resolved", models.DateTimeField(blank=True, null=True)),
                ("message", models.TextField(blank=True, null=True)),
                ("external_id", models.CharField(db_index=True, max_length=190)),
                (
                    "incident",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.incident"
                    ),
                ),
            ],
            options={
                "verbose_name": "Incoming alert",
                "verbose_name_plural": "Incoming alerts",
            },
        ),
    ]
