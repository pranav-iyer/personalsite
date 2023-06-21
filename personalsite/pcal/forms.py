from django import forms

from .models import INTERVAL_UNIT_CHOICES

WEEKDAY_EVERY_CHOICES = [
    (1, "single"),
    (2, "other"),
    (3, "3rd"),
    (4, "4th"),
    (5, "5th"),
    (6, "6th"),
    (7, "7th"),
    (8, "8th"),
    (9, "9th"),
    (10, "10th"),
]


class AddEventForm(forms.Form):
    title = forms.CharField(
        max_length=300,
        widget=forms.TextInput(attrs={"class": "form-control form-control-sm"}),
    )
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control form-control-sm", "type": "date"},
        ),
        required=False,
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={"class": "form-control form-control-sm", "type": "time"}
        ),
        required=False,
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={"class": "form-control form-control-sm", "type": "time"}
        ),
        required=False,
    )
    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control form-control-sm", "type": "date"},
        ),
        required=False,
    )
    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control form-control-sm", "type": "date"},
        ),
        required=False,
    )
    use_date_range = forms.BooleanField(required=False)
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control form-control-sm", "rows": "4"}
        ),
        required=False,
    )
    is_recurring = forms.BooleanField(required=False)
    interval_recurrence_every = forms.IntegerField(
        widget=forms.TextInput(
            attrs={"class": "form-control form-control-sm mx-2", "type": "number"},
        ),
        initial=1,
        min_value=1,
        required=False,
    )
    interval_recurrence_unit = forms.ChoiceField(
        choices=INTERVAL_UNIT_CHOICES,
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
        initial="weeks",
        required=False,
    )
    use_weekday_recurrence = forms.BooleanField(required=False)
    weekday_recurrence_every = forms.ChoiceField(
        choices=WEEKDAY_EVERY_CHOICES,
        widget=forms.Select(attrs={"class": "form-select form-select-sm mx-2"}),
        initial=1,
        required=False,
    )
    weekday_recurrence_weekdays = forms.CharField(
        max_length=7,
        min_length=7,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control form-control-sm"}),
    )
    recurrence_end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control form-control-sm", "type": "date"},
        ),
        required=False,
    )
    viewing_week = forms.DateField()
