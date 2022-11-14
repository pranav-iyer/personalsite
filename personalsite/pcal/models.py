from django.db import models
from django.core.validators import MinValueValidator, RegexValidator

# Create your models here.
"""

RecurrenceData:
    interval_schedule
    weekday_schedule
    start_date
    end_date

IntervalSchedule(RecurrenceSchedule):
    every
    unit (days, weeks, months, years)

WeekdaySchedule(RecurrenceSchedule):
    every
    weekdays (0010100)

"""

INTERVAL_UNIT_CHOICES = [
    ("days", "Days"),
    ("weeks", "Weeks"),
    ("months", "Months"),
    ("years", "Years"),
]

WEEKDAY_NAMES = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]


class TimeRange(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f'{self.date.strftime("%m/%d/%Y")}: {self.start_time.strftime("%H:%M")}-{self.end_time.strftime("%H:%M")}'


class DateRange(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f'{self.start_date.strftime("%m/%d/%Y")} - {self.end_date.strftime("%m/%d/%Y")}'


class IntervalSchedule(models.Model):
    every = models.IntegerField(validators=[MinValueValidator(1)])
    unit = models.CharField(max_length=6, choices=INTERVAL_UNIT_CHOICES)

    def __str__(self) -> str:
        return f"Every {self.every} {self.get_unit_display()}"


class WeekdaySchedule(models.Model):
    """weekdays is a string of length 7, only 0's and 1's, where if the i-th character
    is 1, then that day is included in the recurrence."""

    every = models.IntegerField(validators=[MinValueValidator(1)])
    weekdays = models.CharField(
        max_length=7, validators=[RegexValidator(r"^(0|1){7}$")]
    )

    def __str__(self):
        day_names = ", ".join(
            WEEKDAY_NAMES[i] for i, c in enumerate(self.weekdays) if c == "1"
        )
        return f"Every {self.every} {day_names}"


class RecurrenceData(models.Model):
    interval_schedule = models.ForeignKey(
        IntervalSchedule, on_delete=models.PROTECT, null=True, blank=True
    )
    weekday_schedule = models.ForeignKey(
        WeekdaySchedule, on_delete=models.PROTECT, null=True, blank=True
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        if self.interval_schedule is not None:
            if self.end_date is not None:
                return f"{self.interval_schedule} ({self.start_date.strftime('%m/%d/%Y')}-{self.end_date.strftime('%m/%d/%Y')})"
            else:
                return f"{self.interval_schedule} ({self.start_date.strftime('%m/%d/%Y')}-)"
        else:
            if self.end_date is not None:
                return f"{self.weekday_schedule} ({self.start_date.strftime('%m/%d/%Y')}-{self.end_date.strftime('%m/%d/%Y')})"
            else:
                return (
                    f"{self.weekday_schedule} ({self.start_date.strftime('%m/%d/%Y')}-)"
                )


class Event(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    time_range = models.ForeignKey(
        TimeRange, on_delete=models.PROTECT, null=True, blank=True
    )
    date_range = models.ForeignKey(
        DateRange, on_delete=models.PROTECT, null=True, blank=True
    )
    recurrence_data = models.ForeignKey(
        RecurrenceData, on_delete=models.PROTECT, null=True, blank=True
    )

    @property
    def start_date(self):
        if self.time_range is not None:
            return self.time_range.date
        else:
            return self.date_range.start_date

    @property
    def end_date(self):
        if self.time_range is not None:
            return self.time_range.date
        else:
            return self.date_range.end_date

    @property
    def num_days(self):
        if self.time_range is not None:
            return 0
        else:
            return (self.date_range.end_date - self.date_range.start_date).days

    def __str__(self):
        if self.time_range is not None:
            return self.title + " - " + self.time_range.date.strftime("%m/%d/%Y")
        else:
            return self.title + " - " + self.date_range.start_date.strftime("%m/%d/%Y")

    def get_absolute_url(self):
        from django.urls import reverse_lazy

        return reverse_lazy("pcal:event", kwargs={"pk": self.pk})
