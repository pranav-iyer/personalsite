# Generated by Django 3.2.7 on 2021-10-14 21:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("groceries", "0007_alter_glistitem_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="glist",
            name="updated",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
