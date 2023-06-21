from django.contrib import admin

from .models import MonthlyLimit, Transaction

# Register your models here.
admin.site.register(Transaction)
admin.site.register(MonthlyLimit)
