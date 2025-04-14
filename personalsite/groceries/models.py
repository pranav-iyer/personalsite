from django.db import models

# Create your models here.
"""
class List
    title
    created
    updated
    completed
    contents
    
"""


class GList(models.Model):
    title = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    completed = models.DateTimeField(null=True, blank=True)
    contents = models.TextField()
    checked_index = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def items(self):
        return self.contents.strip().split("\n")

    @property
    def checked_items(self):
        if self.checked_index is not None:
            return self.items[: self.checked_index]
        else:
            return self.items

    @property
    def unchecked_items(self):
        if self.checked_index is not None:
            return self.items[self.checked_index :]
        else:
            return []


##################################################################################
"""
class Item(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name

class GList(models.Model):
    title = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    groceries = models.ManyToManyField(Item, related_name='lists', blank=True, through='GListItem')

    class Meta:
        verbose_name = "grocery list"
        verbose_name_plural = "grocery lists"

    def __str__(self):
        return self.title + " - " + self.created.strftime('%m/%d/%Y %H:%M')

class GListItem(models.Model):
    glist = models.ForeignKey(GList, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    order_in_list = models.IntegerField()
    gotten = models.BooleanField(default=False)

class Store(models.Model):
    name = models.CharField(max_length=300)
    address = models.CharField(max_length=300)

    def __str__(self):
        return self.name + ' - ' + self.address

class Trip(models.Model):
    glist = models.OneToOneField(
        GList,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='trip',
    )
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True)
    completed = models.DateTimeField(null=True, blank=True)
    unlisted_groceries = models.ManyToManyField(Item, related_name='unlisted_trips', blank=True)

    def __str__(self):
        if not self.completed:
            return self.glist.title + ' - not completed'
        else:
            return self.glist.title + ' - ' + self.completed.strftime('%m/%d/%Y %H:%M')

class AisleLocation(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='aisle_locations')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='aisle_locations')
    aisle = models.CharField(max_length=300)

    def __str__(self):
        return self.item.name + ' - ' + self.store.name

"""
