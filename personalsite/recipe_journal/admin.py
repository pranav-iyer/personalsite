from django.contrib import admin
from .models import Recipe, RecipeJournalEntry

# Register your models here.
admin.site.register(Recipe)
admin.site.register(RecipeJournalEntry)