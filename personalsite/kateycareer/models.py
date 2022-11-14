from django.db import models
from django import forms

# Create your models here.
class CareerInfo(models.Model):
    job_title = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job_title
