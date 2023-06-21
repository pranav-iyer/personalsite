from datetime import datetime, timedelta
from django.utils import timezone
import calendar
import pytz

TIMING_CHOICES = [
    ("half_hour", "In 30 Minutes"),
    ("one_hour", "In One Hour"),
    ("four_hours", "In Four Hours"),
    ("eod", "At 11:30PM Tonight"),
    ("tomorrow", "At 8:30AM Tomorrow Morning"),
    ("monday", "At 9:30AM Monday Morning"),
    ("one_week", "In One Week"),
    ("one_month", "In One Month"),
    ("custom", "Custom Time (specify below)"),
]


def get_eta(time_code, custom_time=None):
    """Computes the ETA for the task, based on the time code chosen
    from TIMING_CHOICES (above)."""
    now = timezone.now().astimezone(pytz.timezone("US/Eastern"))
    if time_code == "half_hour":
        chosen_dt = now + timedelta(minutes=30)
    elif time_code == "one_hour":
        chosen_dt = now + timedelta(minutes=60)
    elif time_code == "four_hours":
        chosen_dt = now + timedelta(minutes=240)
    elif time_code == "eod":
        chosen_dt = datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=23,
            minute=30,
            tzinfo=pytz.timezone("US/Eastern"),
        )
        if now.hour == 23 and now.minute >= 30:
            chosen_dt += timedelta(days=1)
    elif time_code == "tomorrow":
        chosen_dt = datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=8,
            minute=30,
            tzinfo=pytz.timezone("US/Eastern"),
        ) + timedelta(days=1)
    elif time_code == "monday":
        chosen_dt = datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=8,
            minute=30,
            tzinfo=pytz.timezone("US/Eastern"),
        ) + timedelta(days=(7 - now.weekday()))
    elif time_code == "one_week":
        chosen_dt = now + timedelta(days=7)
    elif time_code == "one_month":
        chosen_dt = now + timedelta(days=calendar.monthrange(now.year, now.month)[1])
    elif time_code == "custom":
        if custom_time is None:
            raise ValueError(
                "If time_code is 'custom', then a custom datetime must be specified."
            )
        chosen_dt = custom_time
    else:
        raise ValueError(
            f"time_code '{time_code}' is not a valid time_code. Choose from:\n{set(x[0] for x in TIMING_CHOICES)}."
        )

    return chosen_dt
