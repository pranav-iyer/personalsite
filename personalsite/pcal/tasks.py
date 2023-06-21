import calendar
import re
from datetime import date, datetime, timedelta

from celery import shared_task
from django.utils import timezone

from .models import RecurrenceData
from .views import check_event_exists, create_event_instance


# should be run every now and then to make sure that
# recurring tasks are properly updated
@shared_task()
def update_recurring_tasks_without_end_date():
    rdatas = RecurrenceData.objects.filter(end_date__isnull=True)
    now = timezone.now()
    for rdata in rdatas:
        rec_start = rdata.start_date
        rec_end = date(now.year + 1, 12, 31)
        first_event = rdata.event_set.earliest(
            "time_range__date", "date_range__start_date"
        )
        if rdata.weekday_schedule is not None:
            starting_sunday = (
                rec_start
                if rec_start.weekday() == 6
                else rec_start - timedelta(days=rec_start.weekday() + 1)
            )
            ending_sunday = (
                rec_end
                if rec_end.weekday() == 6
                else rec_end - timedelta(days=rec_end.weekday() + 1)
            )

            days_to_recur = [
                m.start() for m in re.finditer("1", rdata.weekday_schedule.weekdays)
            ]

            sunday = starting_sunday
            while sunday <= ending_sunday:
                for idx in days_to_recur:
                    curr_date = sunday + timedelta(days=idx)

                    # check for existing events
                    if curr_date <= rec_end and not check_event_exists(
                        rdata, curr_date
                    ):
                        # create this week's events
                        create_event_instance(first_event, curr_date)
                sunday += timedelta(days=7 * rdata.weekday_schedule.every)
        else:
            unit = rdata.interval_schedule.unit
            if unit == "days":
                curr_date = rec_start
                while curr_date <= rec_end:
                    if not check_event_exists(rdata, curr_date):
                        create_event_instance(first_event, curr_date)
                    curr_date += timedelta(days=rdata.interval_schedule.every)
            elif unit == "weeks":
                curr_date = rec_start
                while curr_date <= rec_end:
                    if not check_event_exists(rdata, curr_date):
                        create_event_instance(first_event, curr_date)
                    curr_date += timedelta(days=7 * rdata.interval_schedule.every)
            elif unit == "months":
                curr_date = rec_start
                curr_day = rec_start.day
                while curr_date <= rec_end:
                    if not check_event_exists(rdata, curr_date):
                        create_event_instance(first_event, curr_date)

                    if curr_date.month == 12:
                        next_year = curr_date.year + 1
                        next_month = 1
                    else:
                        next_year = curr_date.year
                        next_month = curr_date.month + 1

                    if curr_day > calendar.monthrange(next_year, next_month)[1]:
                        next_day = calendar.monthrange(next_year, next_month)[1]
                    else:
                        next_day = curr_day

                    curr_date = datetime(next_year, next_month, next_day)
            elif unit == "years":
                curr_date = rec_start
                while curr_date <= rec_end:
                    if not check_event_exists(rdata, curr_date):
                        create_event_instance(first_event, curr_date)
                    curr_date = datetime(
                        curr_date.year + rdata.interval_schedule.every,
                        curr_date.month,
                        curr_date.day,
                    )
            else:
                raise ValueError(
                    "Interval Recurrence Unit must be one of ('days', 'weeks', 'months', 'years')."
                )
