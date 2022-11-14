import re
from django import forms
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.generic import ListView
from django.utils.html import escape
from django.http import Http404
from django.views.decorators.http import require_POST
from .models import BlogImage, BlogPost
import markdown
from markdown.extensions import Extension
from bs4 import BeautifulSoup


class EscapeHtml(Extension):
    def extendMarkdown(self, md, md_globals):
        del md.preprocessors["html_block"]
        del md.inlinePatterns["html"]


class BlogListView(ListView):
    model = BlogPost
    paginate_by = 5
    context_object_name = "posts"
    template_name = "blog/list.html"

    def get_queryset(self):
        return BlogPost.objects.all().filter(status=1).order_by("-published")


class BlogDraftsView(ListView):
    model = BlogPost
    paginate_by = 10
    context_object_name = "posts"
    template_name = "blog/drafts.html"

    def get_queryset(self):
        return BlogPost.objects.all().filter(status=0).order_by("-updated")


def post_view(request, post_id):
    post = get_object_or_404(BlogPost, pk=post_id)
    if post.status == 1:
        html_text = compile_md(post.text, post.images.all())
        context = {"post": post, "html_text": html_text}
        return render(request, "blog/post.html", context)
    else:
        raise Http404()


def edit_view(request, post_id):
    post = get_object_or_404(BlogPost, pk=post_id)
    if request.method == "POST":
        if "preview-refresh-btn" in request.POST:
            new_title = request.POST["title"]
            new_text = request.POST["text"]
            new_preview = compile_md(new_text, post.images.all())
            context = {
                "post": post,
                "title": new_title,
                "raw_text": new_text,
                "html_preview": new_preview,
                "cursor_pos": request.POST["cursor_pos"],
                "images": post.images.all(),
            }
            context["unsaved"] = (new_title != post.title) or (new_text != post.text)
            return render(request, "blog/edit.html", context)
        elif "save-btn" in request.POST:
            post.text = request.POST["text"]
            post.title = request.POST["title"]
            post.save()
        elif "delete-btn" in request.POST:
            post.delete()
            return redirect("blog:drafts")
        elif "publish-btn" in request.POST:
            post.text = request.POST["text"]
            post.title = request.POST["title"]
            post.save()
            post.publish()
            return redirect(post.get_absolute_url())
    html_text = compile_md(post.text, post.images.all())
    context = {
        "post": post,
        "title": post.title,
        "raw_text": post.text,
        "html_preview": html_text,
        "images": post.images.all(),
    }
    if request.method == "POST":
        context["cursor_pos"] = request.POST["cursor_pos"]
    return render(request, "blog/edit.html", context)


def unpublish_view(request, post_id):
    post = get_object_or_404(BlogPost, pk=post_id)
    post.status = 0
    post.save()
    return redirect(post.get_absolute_url())


def add_view(request):
    post = BlogPost.objects.create(title="Blog Post", text="Write your thoughts here!")
    return redirect(post.get_absolute_url())


def add_image_view(request, post_id):
    post = get_object_or_404(BlogPost, pk=post_id)
    if request.method == "POST":
        form = AddImageForm(request.POST, request.FILES)
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.post = post
            new_image.save()
            return redirect(post.get_absolute_url())
    else:
        form = AddImageForm()
    return render(
        request,
        "blog/add_image.html",
        {"form": form, "post_title": post.title, "post_id": post.id},
    )


def compile_md(raw_text, post_images):
    # preprocess any areas surrounded by triple-backticks into blocks of code for markdown
    chunks = raw_text.split("```")
    res = ""
    for i in range(len(chunks)):
        if i % 2 == 0:
            res += chunks[i]
        else:
            if not (chunks[i].startswith("\n") or chunks[i].startswith("\r\n")):
                res += "    "
            res += "\n    ".join(chunks[i].split("\n"))
    # process markdown
    res = markdown.markdown(res, extensions=[EscapeHtml()])

    soup = BeautifulSoup(res, "html.parser")

    for el in soup("pre"):
        if len(el("code")) == 1:
            el.attrs["class"] = "code-fragment"
            code_el = el("code")[0]
            code_text = code_el.text

            # parse python/js code blocks
            if code_text[:6] == "python":
                code_el.string = code_text[6:].lstrip()
                code_el.attrs["class"] = "language-python"
            elif code_text[:2] == "js":
                code_el.string = code_text[2:].lstrip()
                code_el.attrs["class"] = "language-js"

    for el in soup("code"):
        if el.parent.name.lower() == "pre":
            continue

        el.attrs["class"] = "inline-code"

    # replace p's with div's
    for el in soup("p"):
        el.name = "div"
        if el("img"):
            # add classes for hard-coded images and descriptions
            el.attrs["class"] = "blog-image"
            img, txt = el.children
            el.clear()
            el.append(img)

            desc = soup.new_tag("div")
            desc.string = txt.strip()
            desc.attrs["class"] = "blog-image-desc"
            el.append(desc)

    # expand images
    for image in post_images:
        image_divs = [t.parent for t in soup(text=f"{{{image.slug}}}")]
        for div in image_divs:
            div.attrs["class"] = "blog-image"
            div.clear()

            img = soup.new_tag("img")
            img.attrs["src"] = image.image.url
            img.attrs["alt"] = image.alt_text
            div.append(img)

            desc = soup.new_tag("div")
            desc.string = image.description
            desc.attrs["class"] = "blog-image-desc"
            div.append(desc)

    # replace headings with one lower level (e.g. h1->h2)
    for el in soup("h4"):
        el.name = "h5"

    for el in soup("h3"):
        el.name = "h4"

    for el in soup("h2"):
        el.name = "h3"

    for el in soup("h1"):
        el.name = "h2"
    return str(soup)


class AddImageForm(forms.ModelForm):
    class Meta:
        model = BlogImage
        fields = ["slug", "description", "alt_text", "image"]
        widgets = {
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "alt_text": forms.Textarea(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }
