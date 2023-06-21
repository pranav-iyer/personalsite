from django.db import models


# Create your models here.
class YesItem(models.Model):
    info = models.CharField(max_length=300, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    completed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.info
