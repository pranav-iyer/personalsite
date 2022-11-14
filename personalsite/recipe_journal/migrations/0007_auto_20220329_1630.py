# Generated by Django 3.2.9 on 2022-03-29 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_journal', '0006_alter_recipe_photo'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='recipe',
            name='photo_or_url',
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('url__in', ['', None]), models.Q(('photo__in', ['', None]), _negated=True)), models.Q(('photo__in', ['', None]), models.Q(('url__in', ['', None]), _negated=True)), _connector='OR'), name='photo_or_url'),
        ),
    ]
