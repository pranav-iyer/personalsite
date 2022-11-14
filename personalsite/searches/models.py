from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Search(models.Model):
    text = models.CharField(max_length=1024)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.text