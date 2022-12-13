from django.contrib import admin

from .models import Entry, EntryContent, EntryImage, Feed, FeedGroup

# Register your models here.
admin.site.register(Entry)
admin.site.register(EntryContent)
admin.site.register(EntryImage)
admin.site.register(Feed)
admin.site.register(FeedGroup)
