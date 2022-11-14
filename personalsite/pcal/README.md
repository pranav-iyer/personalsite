# pCal

## Notes

Recurrences can have an end date specified. If they do not, then events are created until the end of next year.
A celery-beat job should be scheduled so that every month or so, events with no recurrence end date are updated to the following year.