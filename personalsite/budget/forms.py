from django import forms


class TransactionReportForm(forms.Form):
    month = forms.ChoiceField(
        choices=[
            (1, "January"),
            (2, "February"),
            (3, "March"),
            (4, "April"),
            (5, "May"),
            (6, "June"),
            (7, "July"),
            (8, "August"),
            (9, "September"),
            (10, "October"),
            (11, "November"),
            (12, "December"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    year = forms.ChoiceField(
        choices=[
            (2021, "2021"),
            (2022, "2022"),
            (2023, "2023"),
            (2024, "2024"),
            (2025, "2025"),
            (2026, "2026"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class CSVDropForm(forms.Form):
    csv_file = forms.FileField(widget=forms.FileInput(attrs={"class": "form-control"}))
    source = forms.ChoiceField(
        choices=[
            ("Already Processed", "Already Processed"),
            ("Pranav Discover", "Pranav Discover"),
            ("Katey Discover", "Katey Discover"),
            ("Katey CapitalOne", "Katey CapitalOne"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class CSVDropSaveForm(forms.Form):
    transactions = forms.JSONField()
