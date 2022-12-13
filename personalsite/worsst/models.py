from django.db import models


# Create your models here.
class FeedGroup(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self) -> str:
        return self.name


class Feed(models.Model):
    feed_group = models.ForeignKey(
        FeedGroup, null=True, blank=True, on_delete=models.SET_NULL
    )
    name = models.CharField(max_length=300)
    xml_url = models.URLField()
    etag = models.CharField(max_length=300, blank=True)
    last_modified = models.DateTimeField(blank=True, null=True)
    html_url = models.URLField(blank=True)

    def __str__(self) -> str:
        return self.name


class Entry(models.Model):
    feed = models.ForeignKey(Feed, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    link = models.URLField()
    published = models.DateTimeField(null=True, blank=True)
    updated = models.DateTimeField(null=True, blank=True)
    author = models.CharField(max_length=300, blank=True)

    def __str__(self) -> str:
        return self.title


class EntryContent(models.Model):
    entry = models.ForeignKey(Entry, null=True, on_delete=models.SET_NULL)
    content_type = models.CharField(max_length=300, blank=True)
    language = models.CharField(max_length=300, blank=True)
    content = models.TextField()
    comparison_hash = models.CharField(max_length=300, blank=True)

    def __str__(self) -> str:
        return f"{self.entry} - {self.comparison_hash[:10]}"


class EntryImage(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    length = models.IntegerField(null=True, blank=True)
    content_type = models.CharField(max_length=300, blank=True)
    title = models.CharField(max_length=300, blank=True)
    href = models.URLField()

    def __str__(self) -> str:
        return f"{self.entry} - {self.title}"


class ReadEvent(models.Model):
    entry = models.ForeignKey(Entry, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=300)
    link = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.entry} - {self.timestamp.strftime('%m/%d/%Y')}"
