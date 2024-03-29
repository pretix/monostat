# Generated by Django 5.0 on 2024-02-11 20:35

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0002_notificationconfiguration_allow_subscriptions"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscriber",
            name="created",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
