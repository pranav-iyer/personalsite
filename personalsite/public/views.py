import unicodedata as ud

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import EmailMultiAlternatives
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

FAV_CHARS = [
    "⌂",
    "⍥",
    "⍾",
    "–",
    "—",
    "␣",
    "‖",
    "⌇",
    "⌤",
    "°",
    "℃",
    "℉",
    "«",
    "»",
    "©",
    "®",
    "™",
    "·",
    "∙",
    "•",
    "∘",
    "⏣",
    "⌑",
    "‣",
    "⁌",
    "⁍",
    "⋆",
    "∗",
    "⁕",
    "⋇",
    "…",
    "±",
    "×",
    "÷",
    "∞",
    "≟",
    "‽",
    "←",
    "↑",
    "→",
    "↓",
    "↔",
    "↕",
    "⇌",
    "⇐",
    "⇑",
    "⇒",
    "⇓",
    "⇔",
    "⇕",
    "⇖",
    "⇗",
    "⇘",
    "⇙",
    "⇜",
    "⇝",
]


# Create your views here.
def fav_chars(request):
    context = {}
    context["favchars"] = [
        {
            "char": c,
            "name": ud.name(c),
            "ord": ord(c),
            "hex": hex(ord(c))[2:].upper().zfill(4),
        }
        for c in FAV_CHARS
    ]
    return render(request, "public/fav_chars.html", context)


def ip_echo(request: HttpRequest):
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(",")[0]
    else:
        client_ip = request.META.get("REMOTE_ADDR", "")
    return HttpResponse(client_ip)


def request_account(request):
    if request.method == "POST":
        name_form = NameForm(request.POST)
        form = UserCreationForm(request.POST)
        if form.is_valid() and name_form.is_valid():
            # save new user, but make them inactive
            new_user = form.save()
            new_user.first_name = name_form.cleaned_data["first_name"]
            new_user.last_name = name_form.cleaned_data["last_name"]
            new_user.email = name_form.cleaned_data["email"]
            new_user.is_active = False
            new_user.is_staff = False
            new_user.is_superuser = False
            new_user.save()

            # send email to admin notifying of new user
            # send email notifying of the new request, along with the zip file attached.
            text_content = f"New User Account Request on pranaviyer.com:\n\nFirst Name: {new_user.first_name}\nLast Name: {new_user.last_name}\nEmail: {new_user.email}\nUsername: {new_user.username}\n\nIf you would like to approve this user's request, visit the admin dashboard and activate their account here:\n\nhttps://pranaviyer.com/admin/auth/user/{new_user.id}/change/"
            html_content = f"""<p>New User Account Request on pranaviyer.com:</p>
            <p>
            <b>First Name:</b> {new_user.first_name}<br>
            <b>Last Name:</b> {new_user.last_name}<br>
            <b>Email:</b> {new_user.email}<br>
            <b>Username:</b> {new_user.username}
            </p>
            <p>If you would like to approve this user's request, visit the admin dashboard and activate their account here:\n\nhttps://pranaviyer.com/admin/auth/user/{new_user.id}/change/</p>
            """
            email = EmailMultiAlternatives(
                f"[pranaviyer.com] New Account Request",
                text_content,
                None,
                ["mail@pranaviyer.com"],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            return redirect("public:index")
    else:
        name_form = NameForm()
        form = UserCreationForm()
    return render(
        request, "public/request_account.html", {"form": form, "name_form": name_form}
    )


class NameForm(forms.Form):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "given-name",
                "autofocus": "autofocus",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={"class": "form-control", "autocomplete": "family-name"}
        ),
    )
    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "autocomplete": "email"}
        )
    )
