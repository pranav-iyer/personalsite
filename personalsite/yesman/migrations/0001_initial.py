# Generated by Django 3.2.9 on 2021-12-09 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='YesItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('info', models.CharField(max_length=300)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('completed', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
