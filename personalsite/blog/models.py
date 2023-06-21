from django.db import models
from django.utils import timezone

STATUSES = ((0, "draft"), (1, "published"))


# Create your models here.
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(choices=STATUSES, default=0)

    def publish(self):
        if self.status != 1:
            self.status = 1
            self.published = timezone.now()
            self.save()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        if self.status == 1:
            return reverse("blog:post", kwargs={"post_id": self.id})
        else:
            return reverse("blog:edit", kwargs={"post_id": self.id})


class BlogImage(models.Model):
    slug = models.SlugField()
    description = models.TextField()
    alt_text = models.TextField()
    image = models.ImageField(upload_to="blog/images/")
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="images")

    def __str__(self):
        return self.slug
