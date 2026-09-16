#!/usr/bin/env python3
"""Enrich the generated JOURNEY LENS RSS with verified original photo URLs.

The feed is rebuilt by build.py. This step reads the same story JSON as the site,
adds one RSS enclosure per story with an existing photo, and keeps all other RSS
content and formatting unchanged. No photos are copied or generated.
"""

import html
import json
import mimetypes
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parent
DOMAIN = "https://journey.yagenji.com"
RSS_PATH = ROOT / "rss.xml"
ITEM_RE = re.compile(r"<item>.*?</item>", re.DOTALL)
LINK_RE = re.compile(r"<link>([^<]+)</link>")


def existing_photo(story):
    candidates = [story.get("heroImage")]
    candidates.extend(
        media.get("image")
        for media in (story.get("media") or [])
        if isinstance(media, dict) and media.get("type") == "photo"
    )
    for source in candidates:
        if not isinstance(source, str) or not source:
            continue
        parsed = urlparse(source)
        if parsed.scheme or parsed.netloc:
            if parsed.scheme != "https" or parsed.netloc != "journey.yagenji.com":
                continue
            path = parsed.path
        else:
            path = parsed.path
        if not path.startswith(("/uploads/", "/thumbs/")):
            continue
        if not (ROOT / path.lstrip("/")).is_file():
            continue
        media_type = mimetypes.guess_type(path)[0]
        if media_type not in ("image/jpeg", "image/png", "image/webp", "image/avif"):
            continue
        return urljoin(DOMAIN, path), media_type
    return None


def main():
    stories = {
        story["id"]: story
        for file in (ROOT / "content" / "stories").glob("*.json")
        for story in [json.loads(file.read_text(encoding="utf-8"))]
        if isinstance(story.get("id"), str)
    }
    feed = RSS_PATH.read_text(encoding="utf-8")
    count = 0

    def attach(match):
        nonlocal count
        item = match.group(0)
        if "<enclosure " in item:
            return item
        link_match = LINK_RE.search(item)
        if not link_match:
            return item
        link = urlparse(html.unescape(link_match.group(1).strip()))
        if link.scheme != "https" or link.netloc != "journey.yagenji.com":
            return item
        story_id = link.path.strip("/")
        story = stories.get(story_id)
        photo = existing_photo(story) if story else None
        if not photo:
            return item
        url, media_type = photo
        enclosure = (
            f'<enclosure url="{html.escape(url, quote=True)}" '
            f'length="0" type="{media_type}"/>'
        )
        count += 1
        return item.replace("</item>", f"{enclosure}\n</item>", 1)

    enriched = ITEM_RE.sub(attach, feed)
    ET.fromstring(enriched)  # Do not publish an invalid XML feed.
    if not count and "<enclosure " not in enriched:
        raise RuntimeError("No existing photo was found for any RSS entry")
    if enriched != feed:
        RSS_PATH.write_text(enriched, encoding="utf-8")
    print(f"JOURNEY LENS RSS: added {count} original-photo enclosures")


if __name__ == "__main__":
    main()
