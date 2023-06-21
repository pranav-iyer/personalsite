import json
from zipfile import ZipFile

from django import forms
from django.core.files import File
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.db.utils import IntegrityError
from django.http import FileResponse, JsonResponse
from django.http.response import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import ListView

from .models import ArtPiece, SaveData


# Create your views here.
def image_download_view(request, slug):
    ap = get_object_or_404(ArtPiece, slug=slug)
    return FileResponse(ap.filled_thumbnail, as_attachment=True, filename=f"{slug}.png")


def zipdrop(request):
    if request.method == "POST":
        zippy = ZipFile(request.FILES["zipfile"])
        contents = zippy.namelist()
        if "info.json" not in contents:
            return HttpResponseBadRequest(
                "Zip Archive does not contain an 'info.json' file."
            )

        with zippy.open("info.json") as f:
            info_dict = json.load(f)

        title = info_dict["title"]
        slug = info_dict["slug"]
        pixart_fnam = info_dict["pixart_file"]
        thumb_fnam = info_dict["thumb_file"]
        thumb_gs_fnam = info_dict["thumb_gs_file"]

        if ArtPiece.objects.filter(slug=slug).exists():
            return HttpResponseBadRequest(
                f"Slug '{slug}' is already in use. Please choose a different slug and try again."
            )

        if not pixart_fnam in contents:
            return HttpResponseBadRequest(
                f"Zip Archive does not contain a {pixart_fnam} file."
            )
        if not thumb_fnam in contents:
            return HttpResponseBadRequest(
                f"Zip Archive does not contain a {thumb_fnam} file."
            )
        if not thumb_gs_fnam in contents:
            return HttpResponseBadRequest(
                f"Zip Archive does not contain a {thumb_gs_fnam} file."
            )

        if request.user.is_staff:
            with zippy.open(pixart_fnam) as pixart_file, zippy.open(
                thumb_gs_fnam
            ) as empty_thumb_file, zippy.open(thumb_fnam) as filled_thumb_file:
                try:
                    ArtPiece.objects.create(
                        title=title,
                        slug=slug,
                        pixart=File(pixart_file, name=pixart_fnam),
                        thumbnail=File(empty_thumb_file, name=thumb_gs_fnam),
                        filled_thumbnail=File(filled_thumb_file, name=thumb_fnam),
                    )
                except IntegrityError:
                    return HttpResponseBadRequest(
                        f"Slug '{slug}' is already in use. Please choose a different slug and try again."
                    )
        else:
            # send email notifying of the new request, along with the zip file attached.
            text_content = f"User '{request.user}' is requesting to add the attached PixelArt, entitled '{title}' to the pranaviyer.com library."
            html_content = f"""User <b>{request.user}</b> is request to add the atttached PixelArt, <b>{title}</b>, to the pranaviyer.com library."""
            email = EmailMultiAlternatives(
                f"[pranaviyer.com] New PixelArt Request from '{request.user}'",
                text_content,
                None,
                ["mail@pranaviyer.com"],
            )
            email.attach_alternative(html_content, "text/html")
            request.FILES["zipfile"].seek(0)
            email.attach(
                f"{title}.zip", request.FILES["zipfile"].read(), "application/zip"
            )
            email.send()
        return JsonResponse({"zipfile": "Good"})
    else:
        raise Http404


def editor_view(request):
    context = {"user_is_staff": request.user.is_staff}
    return render(request, "pixelart/editor.html", context)


def demo_view(request):
    return render(request, "pixelart/demo.html")


def draw_view(request, slug):
    ap = get_object_or_404(ArtPiece, slug=slug)
    save_data_results = SaveData.objects.filter(user=request.user.id, art_piece=ap.id)
    if not save_data_results:
        new_save_data = SaveData.objects.create(art_piece=ap, user=request.user)
        save_data = new_save_data
    else:
        save_data = save_data_results[0]
    return render(
        request, "pixelart/draw.html", {"art_piece": ap, "save_data": save_data}
    )


def save_view(request):
    if request.method != "POST":
        raise Http404()
    else:
        data = request.POST.copy()
        if "save_id" not in data:
            return HttpResponseBadRequest()
        else:
            save_data = SaveData.objects.get(id=data.get("save_id"))
            data.pop("save_id")
            form = SaveDataForm(data, instance=save_data)
            if form.is_valid():
                form.save()
                return HttpResponse("saved.")
            return HttpResponse("unsaved.")


class SaveDataForm(forms.ModelForm):
    class Meta:
        model = SaveData
        fields = ["art_piece", "user", "statuses", "progress"]


@method_decorator(never_cache, name="dispatch")
class ArtPieceListView(ListView):
    model = ArtPiece
    context_object_name = "art_pieces"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        saves = [
            (ap.savedata_set.filter(user=self.request.user))
            for ap in context["art_pieces"]
        ]
        progresses = [
            int(s[0].progress * 100) if s and s[0].progress else -1 for s in saves
        ]
        context["art_pieces"] = zip(context["art_pieces"], progresses)
        return context
