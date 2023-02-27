from django.db import models


# Create your models here.
class Tidbit(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return (
            self.created.strftime("%m/%d/%y")
            + ": "
            + (
                self.description[:40] + "..."
                if len(self.description) > 40
                else self.description
            )
        )
