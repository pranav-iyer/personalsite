from django import forms


class IndexForm(forms.Form):
    view_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control form-control-sm form-control-inline",
                "type": "date",
            },
        ),
        required=False,
    )
