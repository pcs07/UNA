#!/usr/bin/env python3
"""
UNA — UPSC News Analysis
RSS Feed Fetcher

Fetches articles from major Indian news sources,
filters by UPSC-relevant categories, and saves to data/news.json.

Run: python scripts/fetch_news.py
"""

import json
import hashlib
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import feedparser
except ImportError:
    print("Installing feedparser...")
    os.system(f"{sys.executable} -m pip install feedparser")
    import feedparser

try:
    import requests
except ImportError:
    os.system(f"{sys.executable} -m pip install requests")
    import requests

# ─── RSS Feed Definitions ─────────────────────────────────────────────────────

FEEDS = [
    # ── The Hindu ──────────────────────────────────────────────────────────────
    {
        "url": "https://www.thehindu.com/opinion/editorial/feeder/default.rss",
        "source": "The Hindu", "category": "Editorial",
    },
    {
        "url": "https://www.thehindu.com/opinion/op-ed/feeder/default.rss",
        "source": "The Hindu", "category": "Opinion",
    },
    {
        "url": "https://www.thehindu.com/opinion/feeder/default.rss",
        "source": "The Hindu", "category": "Opinion",
    },
    {
        "url": "https://www.thehindu.com/news/international/feeder/default.rss",
        "source": "The Hindu", "category": "International",
    },
    {
        "url": "https://www.thehindu.com/news/national/feeder/default.rss",
        "source": "The Hindu", "category": "National",
    },
    {
        "url": "https://www.thehindu.com/business/Economy/feeder/default.rss",
        "source": "The Hindu", "category": "Economy",
    },
    {
        "url": "https://www.thehindu.com/sci-tech/science/feeder/default.rss",
        "source": "The Hindu", "category": "Science & Tech",
    },
    {
        "url": "https://www.thehindu.com/sci-tech/technology/feeder/default.rss",
        "source": "The Hindu", "category": "Science & Tech",
    },
    {
        "url": "https://www.thehindu.com/sci-tech/energy-and-environment/feeder/default.rss",
        "source": "The Hindu", "category": "Environment",
    },

    # ── Indian Express ─────────────────────────────────────────────────────────
    {
        "url": "https://indianexpress.com/section/opinion/editorials/feed/",
        "source": "Indian Express", "category": "Editorial",
    },
    {
        "url": "https://indianexpress.com/section/opinion/feed/",
        "source": "Indian Express", "category": "Opinion",
    },
    {
        "url": "https://indianexpress.com/section/world/feed/",
        "source": "Indian Express", "category": "International",
    },
    {
        "url": "https://indianexpress.com/section/india/feed/",
        "source": "Indian Express", "category": "National",
    },
    {
        "url": "https://indianexpress.com/section/business/economy/feed/",
        "source": "Indian Express", "category": "Economy",
    },
    {
        "url": "https://indianexpress.com/section/technology/feed/",
        "source": "Indian Express", "category": "Science & Tech",
    },
    {
        "url": "https://indianexpress.com/section/environment/feed/",
        "source": "Indian Express", "category": "Environment",
    },

    # ── Economic Times ─────────────────────────────────────────────────────────
    {
        "url": "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
        "source": "Economic Times", "category": "Economy",
    },
    {
        "url": "https://economictimes.indiatimes.com/news/economy/policy/rssfeeds/1017770097.cms",
        "source": "Economic Times", "category": "Economy",
    },
    {
        "url": "https://economictimes.indiatimes.com/news/politics-and-nation/rssfeeds/1052732854.cms",
        "source": "Economic Times", "category": "National",
    },
    {
        "url": "https://economictimes.indiatimes.com/news/international/rssfeeds/1052732866.cms",
        "source": "Economic Times", "category": "International",
    },
    {
        "url": "https://economictimes.indiatimes.com/tech/rssfeeds/78570561.cms",
        "source": "Economic Times", "category": "Science & Tech",
    },

    # ── Livemint ───────────────────────────────────────────────────────────────
    {
        "url": "https://www.livemint.com/rss/opinion",
        "source": "Livemint", "category": "Opinion",
    },
    {
        "url": "https://www.livemint.com/rss/economy",
        "source": "Livemint", "category": "Economy",
    },
    {
        "url": "https://www.livemint.com/rss/politics",
        "source": "Livemint", "category": "National",
    },
    {
        "url": "https://www.livemint.com/rss/science",
        "source": "Livemint", "category": "Science & Tech",
    },
    {
        "url": "https://www.livemint.com/rss/news",
        "source": "Livemint", "category": "National",
    },

    # ── Business Standard ──────────────────────────────────────────────────────
    {
        "url": "https://www.business-standard.com/rss/home_page_top_stories.rss",
        "source": "Business Standard", "category": "Economy",
    },
    {
        "url": "https://www.business-standard.com/rss/opinion-editorials.rss",
        "source": "Business Standard", "category": "Editorial",
    },
    {
        "url": "https://www.business-standard.com/rss/economy-policy.rss",
        "source": "Business Standard", "category": "Economy",
    },
    {
        "url": "https://www.business-standard.com/rss/international.rss",
        "source": "Business Standard", "category": "International",
    },
    {
        "url": "https://www.business-standard.com/rss/technology.rss",
        "source": "Business Standard", "category": "Science & Tech",
    },
]

# ─── Config ───────────────────────────────────────────────────────────────────

LOOKBACK_DAYS = 3          # fetch articles from last N days
MAX_PER_FEED  = 30         # max articles per feed
OUTPUT_FILE   = Path(__file__).parent.parent / "data" / "news.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; UNA-UPSC-NewsBot/1.0; "
        "+https://github.com/UNA-UPSC)"
    )
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def parse_date(entry) -> datetime | None:
    """Try multiple fields to extract a timezone-aware datetime."""
    for field in ("published_parsed", "updated_parsed", "created_parsed"):
        t = getattr(entry, field, None)
        if t:
            try:
                import time
                ts = time.mktime(t)
                return datetime.fromtimestamp(ts, tz=timezone.utc)
            except Exception:
                pass
    return None


def make_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]


def clean_html(html: str) -> str:
    """Strip HTML tags from description."""
    import re
    if not html:
        return ""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()[:500]


# ─── Fetcher ──────────────────────────────────────────────────────────────────

def fetch_feed(config: dict, cutoff: datetime, seen: set) -> list:
    articles = []
    url = config["url"]

    try:
        # Use requests for better header control, then parse with feedparser
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
    except Exception as e:
        # Fallback: let feedparser handle it directly
        try:
            feed = feedparser.parse(url)
        except Exception as e2:
            print(f"  ✗ {config['source']} [{config['category']}]: {e2}")
            return []

    entries = feed.get("entries", [])[:MAX_PER_FEED]
    count = 0

    for entry in entries:
        url_raw = entry.get("link", "").strip()
        if not url_raw or url_raw in seen:
            continue

        published = parse_date(entry)
        if published and published < cutoff:
            continue  # too old

        title = (entry.get("title") or "").strip()
        if not title:
            continue

        desc = clean_html(
            entry.get("summary") or entry.get("description") or ""
        )

        seen.add(url_raw)
        articles.append({
            "id":          make_id(url_raw),
            "title":       title,
            "description": desc,
            "url":         url_raw,
            "source":      config["source"],
            "category":    config["category"],
            "published":   published.isoformat() if published else None,
        })
        count += 1

    status = "✓" if count > 0 else "○"
    print(f"  {status} {config['source']:20s} [{config['category']:15s}] — {count} articles")
    return articles


def fetch_all() -> list:
    cutoff  = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
    seen    = set()
    all_articles = []

    print(f"\nFetching news from {len(FEEDS)} feeds (last {LOOKBACK_DAYS} days)…\n")

    for config in FEEDS:
        articles = fetch_feed(config, cutoff, seen)
        all_articles.extend(articles)

    # Sort newest first
    all_articles.sort(
        key=lambda a: a["published"] or "0000",
        reverse=True,
    )

    return all_articles


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    articles = fetch_all()

    # Ensure output dir exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Category stats
    from collections import Counter
    cats = Counter(a["category"] for a in articles)
    srcs = Counter(a["source"] for a in articles)

    payload = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total":        len(articles),
        "by_category":  dict(cats),
        "by_source":    dict(srcs),
        "articles":     articles,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\n{'─'*50}")
    print(f"✅ Saved {len(articles)} articles → {OUTPUT_FILE}")
    print(f"\nBy category:")
    for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"   {cat:20s} {n}")
    print(f"\nBy source:")
    for src, n in sorted(srcs.items(), key=lambda x: -x[1]):
        print(f"   {src:20s} {n}")


if __name__ == "__main__":
    main()
