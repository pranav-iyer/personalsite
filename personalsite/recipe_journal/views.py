import io
import os
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.core.files.images import ImageFile
from django.core.files import File
from django.views.decorators.cache import never_cache
from .models import Recipe, RecipeJournalEntry, RecipePhoto
from .forms import RecipeForm, RecipeJournalEntryForm
from PIL import Image, ExifTags


# Create your views here.
def index_view(request):
    context = {"recipes": Recipe.objects.all()}
    return render(request, "recipe_journal/index.html", context)


def recipe_detail_view(request, pk):
    rec = get_object_or_404(Recipe, pk=pk)
    context = {"recipe": rec, "entries": rec.journal_entries.all().order_by("-created")}
    return render(request, "recipe_journal/recipe_detail.html", context)


@never_cache
def recipe_photos_view(request, pk):
    rec = get_object_or_404(Recipe, pk=pk)
    photos = rec.photos.all().order_by("order_in_recipe")
    if len(photos) == 0:
        raise Http404()
    return render(
        request,
        "recipe_journal/recipe_photos.html",
        {"recipe": rec, "photos": photos, "mult_photos": (len(photos) > 1)},
    )


def rotate_right_view(request, pk):
    photo = get_object_or_404(RecipePhoto, pk=pk)
    rotate_right(photo.photo.path)
    photo.save()
    return redirect("recipe_journal:recipe_photos", photo.recipe.pk)


def rotate_left_view(request, pk):
    photo = get_object_or_404(RecipePhoto, pk=pk)
    rotate_left(photo.photo.path)
    photo.save()
    return redirect("recipe_journal:recipe_photos", photo.recipe.pk)


def recipe_text_view(request, pk):
    rec = get_object_or_404(Recipe, pk=pk)
    return render(
        request,
        "recipe_journal/recipe_text.html",
        {
            "recipe": rec,
        },
    )


def add_recipe_view(request):
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data.get("url") != "":
                for i in range(1, 11):
                    form.cleaned_data.pop(f"photo{i}")
                form.cleaned_data.pop("raw_text")
                new_recipe = Recipe.objects.create(**form.cleaned_data)
                new_recipe.save()
            elif form.cleaned_data.get("raw_text") != "":
                for i in range(1, 11):
                    form.cleaned_data.pop(f"photo{i}")
                form.cleaned_data.pop("url")
                new_recipe = Recipe.objects.create(**form.cleaned_data)
                new_recipe.save()
            else:
                form.cleaned_data.pop("url")
                form.cleaned_data.pop("raw_text")
                new_recipe = Recipe.objects.create(title=form.cleaned_data.get("title"))
                new_recipe.save()
                for i in range(1, 11):
                    if form.cleaned_data.get(f"photo{i}") in ["", None]:
                        break
                    new_photo = RecipePhoto.objects.create(
                        recipe=new_recipe,
                        order_in_recipe=i,
                        photo=form.cleaned_data.get(f"photo{i}"),
                    )
                    rotate_exif(new_photo.photo.path)
                    new_photo.save()
            return redirect("recipe_journal:recipe", new_recipe.pk)
    else:
        form = RecipeForm()
    return render(request, "recipe_journal/add_recipe.html", {"form": form})


def add_entry_view(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == "POST":
        form = RecipeJournalEntryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("recipe_journal:recipe", recipe.pk)
    else:
        form = RecipeJournalEntryForm(initial={"recipe": recipe.pk})
    return render(
        request, "recipe_journal/add_entry.html", {"form": form, "recipe": recipe}
    )


def rotate_exif(filepath):
    try:
        image = Image.open(filepath)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == "Orientation":
                break
        exif = dict(image._getexif().items())

        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)
        image.save(filepath)
        image.close()
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass


def rotate_right(filepath):
    image = Image.open(filepath)
    image = image.rotate(270, expand=True)
    image.save(filepath)
    image.close()


def rotate_left(filepath):
    image = Image.open(filepath)
    image = image.rotate(90, expand=True)
    image.save(filepath)
    image.close()
