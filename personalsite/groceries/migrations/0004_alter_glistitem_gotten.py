# Generated by Django 3.2.7 on 2021-09-28 21:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("groceries", "0003_auto_20210928_1716"),
    ]

    operations = [
        migrations.AlterField(
            model_name="glistitem",
            name="gotten",
            field=models.BooleanField(default=False),
        ),
    ]
