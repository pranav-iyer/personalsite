import os
import re
from datetime import datetime
from pathlib import Path
from time import mktime
from typing import Any, Optional

import feedparser
import pytz
import requests
from defusedxml.ElementTree import parse as xmlparse
from django.core.management.base import BaseCommand
from requests.exceptions import Timeout
from worsst.models import Entry, EntryContent, EntryImage, Feed, FeedGroup


def slugify(s: str):
    s = re.sub(r"[^a-zA-Z \-]", "", s)
    s = re.sub(r"\s+", " ", s)
    s = s.replace(" ", "_")
    return s


def process_feed(contents: str, feed: Feed):
    d = feedparser.parse(contents)

    for entr in d.entries:
        title = entr.get("title") or ""
        desc = entr.get("description") or ""
        link = entr.get("link") or ""
        published = entr.get("published_parsed")
        if published is not None:
            published = datetime.fromtimestamp(mktime(published), tz=pytz.UTC)
        updated = entr.get("updated_parsed")
        if updated is not None:
            updated = datetime.fromtimestamp(mktime(updated), tz=pytz.UTC)
        author = entr.get("author") or ""
        entry = Entry.objects.create(
            feed=feed,
            title=title,
            description=desc,
            link=link,
            published=published,
            updated=updated,
            author=author,
        )
        content = entr.get("content")
        if content is not None and len(content) > 0:
            content = content[0]
            EntryContent.objects.create(
                entry=entry,
                content_type=content.get("type") or "",
                language=content.get("language") or "",
                content=content.get("value") or "",
                comparison_hash="",
            )

        # check for images
        image = entr.get("image")
        if image is not None:
            href = image.get("href") or ""
            # also try other aliases
            if not href:
                href = image.get("url") or ""

            if not href:
                href = image.get("link") or ""

            EntryImage.objects.create(
                entry=entry,
                length=image.get("length") or 0,
                content_type=image.get("type") or "",
                title=image.get("title") or "",
                href=href,
            )

        else:
            # maybe its under media content?
            media_content = entr.get("media_content")
            if (
                media_content is not None
                and len(media_content) > 0
                and len(media_content[0])
            ):
                media_info = media_content[0]
                href = media_info.get("url") or ""
                if not href:
                    href = media_info.get("link") or ""

                EntryImage.objects.create(
                    entry=entry,
                    length=media_info.get("length") or 0,
                    content_type=media_info.get("type") or "",
                    title=media_info.get("title") or "",
                    href=href,
                )

            else:
                # a third case .. ?
                pass


def load_subscriptions(filename: str, cache_dir: str):
    root = xmlparse(filename).getroot()
    body = root[1]

    for outline in body:
        group_name = outline.attrib["title"]
        feed_group, _ = FeedGroup.objects.get_or_create(name=group_name)

        for feed in outline:
            feed_title = feed.attrib["title"]
            xml_url = feed.attrib["xmlUrl"]
            html_url = feed.attrib["htmlUrl"]

            if not Feed.objects.filter(xml_url=xml_url).exists():
                feed = Feed.objects.create(
                    feed_group=feed_group,
                    name=feed_title,
                    xml_url=xml_url,
                    etag="",
                    last_modified=None,
                    html_url=html_url,
                )
            else:
                feed = Feed.objects.get(xml_url=xml_url)

            # manual exceptions
            if "foodondemand" in xml_url:
                continue
            if (
                "AFN" in feed_title
                or "Spoon" in feed_title
                or "Scientific American" in feed_title
            ):
                continue
            if "Grist" in feed_title:
                continue

            # get contents of this feed, either from cache, or from xml_url
            cache_fnam = Path(cache_dir) / f"{slugify(feed_title)}.xml"
            if not os.path.exists(cache_fnam):
                print(f"Feed {feed_title!r} not found in cache, fetching...")
                # fetch from server
                try:
                    res = requests.get(xml_url, timeout=10)
                except Timeout:
                    print(f"Request timed out to {xml_url}.")
                    continue

                if not res.ok:
                    print(f"Response returned {res.status_code}.")
                    continue

                with open(cache_fnam, "w") as f:
                    f.write(res.text)

            else:
                print(f"Feed {feed_title!r} found in cache.")

            with open(cache_fnam, "r") as f:
                feed_contents = f.read()

            process_feed(feed_contents, feed)


class Command(BaseCommand):
    help = "Loads in subscription data from a OPML file, and optionally reads from previously loaded XML files."

    def add_arguments(self, parser) -> None:
        parser.add_argument("sub_file")
        parser.add_argument("cache_dir")

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        load_subscriptions(options["sub_file"], options["cache_dir"])
