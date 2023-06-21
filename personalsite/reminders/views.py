from django import forms
from django.shortcuts import redirect, render
from django.utils import timezone

from .scheduling import TIMING_CHOICES, get_eta
from .tasks import schedule_reminder_email, send_reminder_email


# Create your views here.
def create_reminder_view(request):
    if request.method == "POST":
        form = ReminderForm(request.POST)
        if form.is_valid():
            task_eta = get_eta(
                form.cleaned_data["reminder_time"], form.cleaned_data.get("custom_time")
            )

            # send_reminder_email.apply_async(
            #     args=(form.cleaned_data["name_for"], form.cleaned_data["message"]),
            #     eta=task_eta,
            # )

            schedule_reminder_email(
                form.cleaned_data["name_for"], form.cleaned_data["message"], task_eta
            )

            return redirect("reminders:success")
    else:
        form = ReminderForm()
    return render(request, "reminders/create.html", {"form": form})


def success_view(request):
    return render(request, "reminders/success.html")


class ReminderForm(forms.Form):
    name_for = forms.ChoiceField(
        label="Reminder for", choices=[("pranav", "Pranav"), ("katey", "Katey")]
    )
    message = forms.CharField(
        label="Reminder text", widget=forms.Textarea(attrs={"rows": 5})
    )
    reminder_time = forms.ChoiceField(
        label="When do you want to be reminded?",
        choices=TIMING_CHOICES,
    )
    custom_time = forms.DateTimeField(label="Custom Reminder Time", required=False)

    def clean_custom_time(self):
        if self.cleaned_data["custom_time"] is not None:
            if self.cleaned_data["custom_time"] < timezone.now():
                raise forms.ValidationError("Reminder time must be in the future.")

        return self.cleaned_data["custom_time"]

    def clean(self, *args, **kwargs):
        if (
            "reminder_time" in self.cleaned_data
            and self.cleaned_data["reminder_time"] == "custom"
        ):
            if (
                "custom_time" not in self.cleaned_data
                or self.cleaned_data["custom_time"] is None
            ):
                raise forms.ValidationError(
                    "Please specify a custom time to send the reminder."
                )
        super().clean(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if type(visible.field) in [
                forms.fields.CharField,
                forms.fields.DateTimeField,
            ]:
                visible.field.widget.attrs["class"] = "form-control"
            elif type(visible.field) in [forms.fields.ChoiceField]:
                visible.field.widget.attrs["class"] = "form-select"
            elif type(visible.field) in [forms.fields.BooleanField]:
                visible.field.widget.attrs["class"] = "form-check-input"
