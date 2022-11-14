from django.db import models

CATEGORIES = [
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
]

CATEGORIES_REVERSE = dict((x[1], x[0]) for x in CATEGORIES)


class MonthlyLimit(models.Model):
    edited_category = models.CharField(choices=CATEGORIES, max_length=3, unique=True)
    monthly_limit = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.get_edited_category_display()} - {self.monthly_limit}"  # type: ignore


# Create your models here.
class Transaction(models.Model):
    source = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.CharField(max_length=300)
    date = models.DateField()
    category = models.CharField(max_length=50)
    edited_category = models.CharField(
        choices=CATEGORIES,
        max_length=3,
    )
