# Generated by Django 3.2.7 on 2021-09-28 20:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("groceries", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="glist",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
