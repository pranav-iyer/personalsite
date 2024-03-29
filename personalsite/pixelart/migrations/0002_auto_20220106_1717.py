# Generated by Django 3.2.9 on 2022-01-06 22:17

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pixelart", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="artpiece",
            name="created",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="savedata",
            name="updated",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
