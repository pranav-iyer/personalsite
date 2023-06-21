from django import forms
from .models import Tidbit


class TidbitForm(forms.ModelForm):
    class Meta:
        model = Tidbit
        fields = ["description"]
