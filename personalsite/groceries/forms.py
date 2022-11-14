from django import forms
from django.forms import widgets

from .models import GList

class GListForm(forms.ModelForm):
    class Meta:
        model = GList
        fields = ['title', 'contents']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget = forms.TextInput(attrs={"class": "form-control"})
        self.fields["contents"].widget = forms.Textarea(attrs={"class": "form-control"})