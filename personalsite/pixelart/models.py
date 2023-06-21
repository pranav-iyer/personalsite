from django.db import models
from django.contrib.auth.models import User

# Create your models here.
"""
Sketch of models:

ArtPiece:
    pixart = FileField
    thumbnail = ImageField
    title = CharField
    slug = 

SaveData:
    art_piece = ForeignKey(^)
    user = ForeginKey(User)
    statuses = CharField() # maybe there is a betterway to store statuses
    progress = FloatField()
    

"""


class ArtPiece(models.Model):
    pixart = models.FileField(upload_to="pixart/pixart/")
    thumbnail = models.ImageField(upload_to="pixart/thumbnails/", null=True, blank=True)
    filled_thumbnail = models.ImageField(
        upload_to="pixart/thumbnails_filled/", null=True, blank=True
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title


class SaveData(models.Model):
    art_piece = models.ForeignKey(ArtPiece, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    statuses = models.TextField(null=True, blank=True)
    progress = models.FloatField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}-{self.art_piece.title}"
