# Generated by Django 3.2.9 on 2022-08-25 19:37

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("source", models.CharField(max_length=50)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=8)),
                ("description", models.CharField(max_length=300)),
                ("date", models.DateField()),
                ("category", models.CharField(max_length=50)),
                (
                    "edited_category",
                    models.CharField(
                        choices=[
                            ("big", "Big Purchases"),
                            ("car", "Car"),
                            ("cof", "Coffee"),
                            ("fnf", "Fun Food"),
                            ("fns", "Fun Shopping"),
                            ("gro", "Groceries"),
                            ("med", "Medical Services"),
                            ("nos", "Normal Shopping"),
                            ("qum", "Quick Meal"),
                            ("res", "Restaurants"),
                            ("sub", "Subscriptions/Donations"),
                            ("trn", "Transit"),
                            ("trv", "Travel"),
                            ("utl", "Utilities"),
                        ],
                        max_length=3,
                    ),
                ),
            ],
        ),
    ]
