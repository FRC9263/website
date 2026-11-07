"""Fetch the news feeds listed in data/feeds.yaml for the home page.

Headline, source, date and link only. Results are saved to
data/feed_cache.json; if a feed can't be reached, its last good items
from that file are used instead.
"""
import json
import re
import time
import urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

import feedparser
import yaml

ROOT = Path(__file__).parent
CONFIG = ROOT / "data" / "feeds.yaml"
CACHE = ROOT / "data" / "feed_cache.json"
USER_AGENT = "frc9263.ca news page (+https://frc9263.ca)"
PER_FEED = 15  # items kept per feed in the cache


def _download(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def _clean(text):
    """Strip any HTML tags and squash whitespace in a headline."""
    text = re.sub(r"<[^>]+>", "", unescape(text or ""))
    return re.sub(r"\s+", " ", text).strip()


def _when(entry):
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    if not t:
        return None
    return datetime.fromtimestamp(time.mktime(t), tz=timezone.utc).isoformat()


def _fetch_one(feed):
    parsed = feedparser.parse(_download(feed["url"]))
    items = []
    for e in parsed.entries:
        title, link = _clean(e.get("title")), e.get("link", "")
        if not title or not link.startswith("https://"):
            continue  # skip anything odd rather than show a broken link
        items.append({"title": title, "link": link, "source": feed["name"],
                      "group": feed["group"], "date": _when(e)})
        if len(items) >= PER_FEED:
            break
    if not items:
        raise ValueError("feed returned no usable items")
    return items


def _nice_date(iso):
    if not iso:
        return ""
    d = datetime.fromisoformat(iso)
    return f"{d:%b} {d.day}, {d.year}"


def load(fetch=True):
    """Return {"groups": [...], "updated": "..."} for the template."""
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {"feeds": {}}

    for feed in config["feeds"]:
        if not fetch:
            break
        try:
            items = _fetch_one(feed)
            cache["feeds"][feed["url"]] = {"fetched": datetime.now(timezone.utc).isoformat(),
                                           "items": items}
            print(f"  feed ok    {feed['name']}: {len(items)} items")
        except Exception as err:  # keep the last good copy
            kept = len(cache["feeds"].get(feed["url"], {}).get("items", []))
            print(f"  feed FAIL  {feed['name']}: {err} — using {kept} cached items")

    if fetch:
        cache["updated"] = datetime.now(timezone.utc).isoformat()
        CACHE.write_text(json.dumps(cache, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    urls = {f["url"] for f in config["feeds"]}
    everything = [i for u, c in cache["feeds"].items() if u in urls for i in c["items"]]

    groups = []
    for g in config["groups"]:
        cap = g.get("per_source")  # max headlines from any one source (optional)
        seen, per_source, items = set(), {}, []
        for i in sorted((i for i in everything if i["group"] == g["id"]),
                        key=lambda i: i["date"] or "", reverse=True):
            if i["link"] in seen:
                continue
            if cap and per_source.get(i["source"], 0) >= cap:
                continue
            seen.add(i["link"])
            per_source[i["source"]] = per_source.get(i["source"], 0) + 1
            items.append({**i, "nice_date": _nice_date(i["date"])})
        groups.append({**g, "headlines": items[: g.get("show", 5)]})

    return {"groups": groups, "updated": _nice_date(cache.get("updated"))}
