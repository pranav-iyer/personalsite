# Generated by Django 3.2.9 on 2022-03-29 20:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_journal', '0007_auto_20220329_1630'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipePhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(upload_to='recipe_journal/recipe_images/')),
                ('order_in_recipe', models.IntegerField()),
            ],
        ),
        migrations.RemoveConstraint(
            model_name='recipe',
            name='photo_or_url',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='photo',
        ),
        migrations.AddField(
            model_name='recipe',
            name='raw_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='recipephoto',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='recipe_journal.recipe'),
        ),
    ]
