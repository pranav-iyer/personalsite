from django import forms

from .models import RecipeJournalEntry


class RecipeForm(forms.Form):
    title = forms.CharField(max_length=300)
    url = forms.URLField(max_length=300, required=False)
    raw_text = forms.CharField(widget=forms.Textarea, required=False)
    photo1 = forms.ImageField(required=False)
    photo2 = forms.ImageField(required=False)
    photo3 = forms.ImageField(required=False)
    photo4 = forms.ImageField(required=False)
    photo5 = forms.ImageField(required=False)
    photo6 = forms.ImageField(required=False)
    photo7 = forms.ImageField(required=False)
    photo8 = forms.ImageField(required=False)
    photo9 = forms.ImageField(required=False)
    photo10 = forms.ImageField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data.get("photo1") is None
            and cleaned_data.get("url") == ""
            and cleaned_data.get("raw_text") == ""
        ):
            raise forms.ValidationError(
                "Either specify a URL, text, or upload one or more images."
            )
        if cleaned_data.get("photo1") is not None and (
            cleaned_data.get("url") != "" or cleaned_data.get("raw_text") != ""
        ):
            raise forms.ValidationError(
                "Either specify a URL, enter recipe text, or upload an image, but not more than one."
            )
        if cleaned_data.get("url") != "" and cleaned_data.get("raw_text") != "":
            raise forms.ValidationError(
                "Either specify a URL, enter recipe text, or upload an image, but not more than one."
            )

        return cleaned_data


class RecipeJournalEntryForm(forms.ModelForm):
    class Meta:
        model = RecipeJournalEntry
        fields = ["recipe", "notes"]
