from django.db import models

# Create your models here.
class Recipe(models.Model):
    title = models.CharField(max_length=300)
    url = models.URLField(max_length=300, null=True, blank=True)
    raw_text = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

class RecipePhoto(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="photos")
    photo = models.ImageField(upload_to="recipe_journal/recipe_images/")
    order_in_recipe = models.IntegerField()

    def __str__(self):
        return f"{self.recipe.title} — Image {self.order_in_recipe}"
    
class RecipeJournalEntry(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="journal_entries")
    created = models.DateTimeField(auto_now_add=True)
    notes = models.TextField()

    def __str__(self):
        return f"{self.recipe.title} — {self.created.strftime('%m/%d/%Y')}"