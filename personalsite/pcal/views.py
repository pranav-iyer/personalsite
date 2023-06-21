import calendar
import re
from datetime import date, datetime, time, timedelta

from django.db.models import F, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import AddEventForm
from .models import (DateRange, Event, IntervalSchedule, RecurrenceData,
                     TimeRange, WeekdaySchedule)


def to_twelve_hour(hour):
    """Converts a 24-hour hour to its 12-hour value."""
    if hour < 0:
        raise ValueError("hour must be between 0 and 23, inclusive.")
    elif hour == 0:
        return "12"
    elif hour <= 12:
        return str(hour)
    elif hour <= 23:
        return str(hour - 12)
    else:
        raise ValueError("hour must be between 0 and 23, inclusive.")


def get_time_subtitle(start_time, end_time):
    """Converts a start and end time to a subtitle to mark calendar events.
    Examples:
        12am - 1pm
        8 - 9:30am
    """
    time_subtitle = ""
    if start_time.minute == 0:
        time_subtitle += to_twelve_hour(start_time.hour)
    else:
        time_subtitle += f"{to_twelve_hour(start_time.hour)}:{start_time.minute}"
    if start_time.hour < 12 and end_time.hour >= 12:
        time_subtitle += "am"

    time_subtitle += " - "

    if end_time.minute == 0:
        time_subtitle += to_twelve_hour(end_time.hour)
    else:
        time_subtitle += f"{to_twelve_hour(end_time.hour)}:{end_time.minute}"
    if end_time.hour < 12:
        time_subtitle += "am"
    else:
        time_subtitle += "pm"

    return time_subtitle


def get_time_range_events(dates):
    """List all events with a time range, that fall on a day within the supplied range of dates."""
    time_range_events = []
    for date in dates:
        events = list(
            Event.objects.filter(time_range__date=date)
            .order_by("time_range__start_time")
            .annotate(
                top_pos=(F("time_range__start_time__hour") * 48)
                + (F("time_range__start_time__minute") * 48 / 60),
                height=(
                    (
                        F("time_range__end_time__hour")
                        + (F("time_range__end_time__minute") / 60)
                    )
                    - (
                        F("time_range__start_time__hour")
                        + (F("time_range__start_time__minute") / 60)
                    )
                )
                * 48,
                start_time=F("time_range__start_time"),
                end_time=F("time_range__end_time"),
                date=F("time_range__date"),
            )
            .values()
        )
        for event in events:
            start_time = event["start_time"]
            end_time = event["end_time"]

            event["time_subtitle"] = get_time_subtitle(start_time, end_time)
            event["url"] = reverse("pcal:event", kwargs={"pk": event["id"]})
        time_range_events.append(events)
    return time_range_events


def get_date_range_events(dates):
    """List all events with a date range, that intersect in any way the supplied range of dates."""
    date_range_events = list(
        Event.objects.filter(
            Q(date_range__start_date__range=(dates[0].date(), dates[-1].date()))
            | Q(date_range__end_date__range=(dates[0].date(), dates[-1].date()))
            | Q(
                date_range__start_date__lte=dates[0].date(),
                date_range__end_date__gte=dates[-1].date(),
            )
        )
        .annotate(
            start_date=F("date_range__start_date"),
            end_date=F("date_range__end_date"),
        )
        .values()
    )

    for event in date_range_events:
        clamped_start = max(event["start_date"], dates[0].date())
        clamped_end = min(event["end_date"], dates[-1].date())

        event["left"] = (clamped_start - dates[0].date()).days * (100 / len(dates))
        event["width"] = ((clamped_end - clamped_start).days + 1) * (100 / len(dates))

        event["overflow_start"] = event["start_date"] < dates[0].date()
        event["overflow_end"] = event["end_date"] > dates[-1].date()

    return date_range_events


def check_event_exists(rec_data, target_dtm):
    """Checks if an event starting on the given date exists already for the
    specified recurrence data"""
    return (
        rec_data.event_set.filter(date_range__start_date=target_dtm).exists()
        or rec_data.event_set.filter(time_range__date=target_dtm).exists()
    )


def create_event_instance(template_event, target_dtm):
    """Creates a new event instance with the same data as the template_event,
    except starting at the supplied datetime
    """
    if template_event.date_range is not None:
        new_date_range = DateRange.objects.create(
            start_date=target_dtm,
            end_fill=target_dtm + timedelta(days=template_event.num_days),
        )
        Event.objects.create(
            title=template_event.title,
            description=template_event.description,
            date_range=new_date_range,
            recurrence_data=template_event.recurrence_data,
        )
    else:
        new_time_range = TimeRange.objects.create(
            date=target_dtm,
            start_time=template_event.time_range.start_time,
            end_time=template_event.time_range.end_time,
        )
        Event.objects.create(
            title=template_event.title,
            description=template_event.description,
            time_range=new_time_range,
            recurrence_data=template_event.recurrence_data,
        )


# Create your views here.
def home_view(request):
    now = timezone.now()
    return redirect("pcal:week", now.year, now.month, now.day)


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, "pcal/event_detail.html", {"event": event})


def add_event(request):
    if request.method == "POST":
        form = AddEventForm(request.POST)
        if form.is_valid():
            # build recurrence data
            if form.cleaned_data["is_recurring"]:
                recurrence_start = (
                    form.cleaned_data["start_date"]
                    if form.cleaned_data["use_date_range"]
                    else form.cleaned_data["date"]
                )

                if form.cleaned_data["use_weekday_recurrence"]:
                    weekday_rec = WeekdaySchedule.objects.create(
                        every=form.cleaned_data["weekday_recurrence_every"],
                        weekdays=form.cleaned_data["weekday_recurrence_weekdays"],
                    )
                    rec_data = RecurrenceData.objects.create(
                        weekday_schedule=weekday_rec,
                        start_date=recurrence_start,
                        end_date=form.cleaned_data["recurrence_end_date"],
                    )
                else:
                    interval_rec = IntervalSchedule.objects.create(
                        every=form.cleaned_data["interval_recurrence_every"],
                        unit=form.cleaned_data["interval_recurrence_unit"],
                    )
                    rec_data = RecurrenceData.objects.create(
                        interval_schedule=interval_rec,
                        start_date=recurrence_start,
                        end_date=form.cleaned_data["recurrence_end_date"],
                    )
            else:
                rec_data = None

            if form.cleaned_data["use_date_range"]:
                num_days = (
                    form.cleaned_data["end_date"] - form.cleaned_data["start_date"]
                ).days
                date_range = DateRange.objects.create(
                    start_date=form.cleaned_data["start_date"],
                    end_date=form.cleaned_data["end_date"],
                )
                event = Event.objects.create(
                    title=form.cleaned_data["title"],
                    description=form.cleaned_data["description"],
                    date_range=date_range,
                    recurrence_data=rec_data,
                )

            else:
                time_range = TimeRange.objects.create(
                    date=form.cleaned_data["date"],
                    start_time=form.cleaned_data["start_time"],
                    end_time=form.cleaned_data["end_time"],
                )
                event = Event.objects.create(
                    title=form.cleaned_data["title"],
                    description=form.cleaned_data["description"],
                    time_range=time_range,
                    recurrence_data=rec_data,
                )

            # create recurring event instances
            if form.cleaned_data["is_recurring"]:
                rec_start = form.cleaned_data["start_date"]
                rec_end = form.cleaned_data["recurrence_end_date"] or date(
                    timezone.now().year + 1, 12, 31
                )
                if form.cleaned_data["use_weekday_recurrence"]:
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
                        m.start()
                        for m in re.finditer(
                            "1", form.cleaned_data["weekday_recurrence_weekdays"]
                        )
                    ]

                    sunday = starting_sunday
                    while sunday <= ending_sunday:
                        for idx in days_to_recur:
                            curr_dtm = sunday + timedelta(days=idx)

                            # check for existing events
                            if curr_dtm <= rec_end and not check_event_exists(
                                rec_data, curr_dtm
                            ):
                                # create this week's events
                                create_event_instance(event, curr_dtm)
                        sunday += timedelta(
                            days=7 * form.cleaned_data["weekday_recurrence_every"]
                        )
                else:
                    if form.cleaned_data["interval_recurrence_unit"] == "days":
                        curr_dtm = rec_start
                        while curr_dtm <= rec_end:
                            if not check_event_exists(rec_data, curr_dtm):
                                create_event_instance(event, curr_dtm)
                            curr_dtm += timedelta(
                                days=form.cleaned_data["interval_recurrence_every"]
                            )
                    elif form.cleaned_data["interval_recurrence_unit"] == "weeks":
                        curr_dtm = rec_start
                        while curr_dtm <= rec_end:
                            if not check_event_exists(rec_data, curr_dtm):
                                create_event_instance(event, curr_dtm)
                            curr_dtm += timedelta(
                                days=7 * form.cleaned_data["interval_recurrence_every"]
                            )
                    elif form.cleaned_data["interval_recurrence_unit"] == "months":
                        curr_dtm = rec_start
                        curr_day = rec_start.day
                        while curr_dtm <= rec_end:
                            if not check_event_exists(rec_data, curr_dtm):
                                create_event_instance(event, curr_dtm)

                            if curr_dtm.month == 12:
                                next_year = curr_dtm.year + 1
                                next_month = 1
                            else:
                                next_year = curr_dtm.year
                                next_month = curr_dtm.month + 1

                            if curr_day > calendar.monthrange(next_year, next_month)[1]:
                                next_day = calendar.monthrange(next_year, next_month)[1]
                            else:
                                next_day = curr_day

                            curr_dtm = datetime(next_year, next_month, next_day)
                    elif form.cleaned_data["interval_recurrence_unit"] == "years":
                        curr_dtm = rec_start
                        while curr_dtm <= rec_end:
                            if not check_event_exists(rec_data, curr_dtm):
                                create_event_instance(event, curr_dtm)
                            curr_dtm = datetime(
                                curr_dtm.year
                                + form.cleaned_data["interval_recurrence_every"],
                                curr_dtm.month,
                                curr_dtm.day,
                            )
                    else:
                        raise ValueError(
                            "Interval Recurrence Unit must be one of ('days', 'weeks', 'months', 'years')."
                        )

            redirect_date = form.cleaned_data["viewing_week"]
            return redirect(
                "pcal:week", redirect_date.year, redirect_date.month, redirect_date.day
            )
    else:
        form = AddEventForm()
    return render(request, "pcal/add_event.html", {"form": form})


def week_view(request, year, month, day):
    # validate date
    if month < 1 or month > 12:
        raise Http404()

    last_day_of_month = calendar.monthrange(year, month)[1]
    if day < 1 or day > last_day_of_month:
        raise Http404()

    dtm = datetime(year, month, day)
    if dtm.weekday() != 6:
        last_sunday = dtm - timedelta(days=dtm.weekday() + 1)
        return redirect(
            "pcal:week", last_sunday.year, last_sunday.month, last_sunday.day
        )

    dates = [dtm + timedelta(days=i) for i in range(7)]
    time_range_events = get_time_range_events(dates)
    date_range_events = get_date_range_events(dates)

    context = {
        "year": year,
        "month": month,
        "day": day,
        "dates": dates,
        "hours": [time(hour=i).strftime("%-I %p") for i in range(24)],
        "prev_sun": dtm - timedelta(days=7),
        "next_sun": dtm + timedelta(days=7),
        "time_range_events": time_range_events,
        "date_range_events": date_range_events,
        "add_event_form": AddEventForm(),
        "title": f"Week of {dtm.strftime('%b %-d, %Y')}",
    }
    return render(request, "pcal/week.html", context)
