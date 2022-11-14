# Generated by Django 3.2.7 on 2021-09-28 23:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('groceries', '0004_alter_glistitem_gotten'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trip',
            name='glist',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='trip', serialize=False, to='groceries.glist'),
        ),
    ]
