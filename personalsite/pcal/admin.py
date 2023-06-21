from django.contrib import admin

from .models import (DateRange, Event, IntervalSchedule, RecurrenceData,
                     TimeRange, WeekdaySchedule)

# Register your models here.
admin.site.register(Event)
admin.site.register(RecurrenceData)
admin.site.register(WeekdaySchedule)
admin.site.register(IntervalSchedule)
admin.site.register(DateRange)
admin.site.register(TimeRange)
