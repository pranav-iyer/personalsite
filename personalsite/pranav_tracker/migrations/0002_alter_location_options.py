# Generated by Django 4.1.9 on 2024-07-29 19:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pranav_tracker', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='location',
            options={'ordering': ['timestamp']},
        ),
    ]