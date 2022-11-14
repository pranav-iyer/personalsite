from django.contrib import admin
from .models import ArtPiece, SaveData

# Register your models here.
class ArtPieceAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(ArtPiece, ArtPieceAdmin)
admin.site.register(SaveData)