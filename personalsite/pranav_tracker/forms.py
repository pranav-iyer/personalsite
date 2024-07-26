from django import forms


class IndexForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control form-control-sm form-control-inline",
                "type": "date",
            },
        ),
        required=False,
    )
    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control form-control-sm form-control-inline",
                "type": "date",
            },
        ),
        required=False,
    )

    def clean(self):
        super().clean()
        end_date = self.cleaned_data["end_date"]
        start_date = self.cleaned_data["start_date"]
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("Start date can't be after end date!")
