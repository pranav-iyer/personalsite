# Generated by Django 3.2.9 on 2022-09-08 14:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("budget", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BudgetLimit",
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
                ("monthly_limit", models.DecimalField(decimal_places=2, max_digits=8)),
            ],
        ),
    ]
