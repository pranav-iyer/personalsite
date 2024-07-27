from django.conf import settings
import json

stylesheets = []


def post_compress_handler(**kwargs):
    if kwargs["type"] != "css":
        return

    global stylesheets
    if kwargs["context"]["compressed"]["name"] == "base":
        stylesheets.append(kwargs["context"]["compressed"]["url"])

    with open(
        settings.BASE_DIR / "pranaviyer-frontend" / "compress_info.json", "w"
    ) as f:
        json.dump({"stylesheets": stylesheets}, f)
