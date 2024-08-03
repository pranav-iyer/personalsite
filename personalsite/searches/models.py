from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Search(models.Model):
    text = models.CharField(max_length=1024)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return self.text
