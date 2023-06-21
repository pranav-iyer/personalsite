from secrets import choice

from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class IngredientType(models.Model):
    class Category(models.TextChoices):
        PRODUCE = "PR"
        BAKERY = "BK"
        MEAT = "MT"
        PREPARED_FOODS = "PF"
        DAIRY = "DA"
        PANTRY = "PA"
        FRIDGE = "RF"
        FROZEN = "FR"
        HOUSEHOLD = "HO"

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=2, choices=Category.choices)
    shelf_life = models.DurationField(null=True, blank=True)

    def __str__(self):
        return self.name


class IngInstance(models.Model):
    class Location(models.TextChoices):
        KATEYS_APT = "KT", _("Katey's Apartment (4225 Baltimore)")
        PRANAVS_APT = "PR", _("Pranav's Apartment (913 Ridge)")

    ing_type = models.ForeignKey(IngredientType, on_delete=models.CASCADE)
    exists = models.BooleanField()
    quantity = models.CharField(max_length=200)
    location = models.CharField(max_length=2, choices=Location.choices)
    created = models.DateTimeField()

    def __str__(self):
        return f"{self.ing_type.name} - {self.created.strftime('%m/%d/%Y')}"
