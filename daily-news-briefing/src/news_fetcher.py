import json
import logging
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# IST offset
IST = timezone(timedelta(hours=5, minutes=30))


class NewsFetcher:
    """Fetches news from multiple free sources (HackerNews API, RSS feeds)."""

    # RSS feeds grouped by topic
    RSS_SOURCES = {
        "AI / Machine Learning": [
            ("MIT Tech Review AI", "https://www.technologyreview.com/feed/"),
            ("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
            ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
        ],
        "Startups / Funding": [
            ("TechCrunch", "https://techcrunch.com/feed/"),
            ("YC Blog", "https://www.ycombinator.com/blog/rss/"),
        ],
        "Indian Tech / Business": [
            ("Inc42", "https://inc42.com/feed/"),
            ("YourStory", "https://yourstory.com/feed"),
        ],
        "Tech Industry": [
            ("The Verge", "https://www.theverge.com/rss/index.xml"),
            ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
        ],
    }

    def __init__(self):
        self.all_stories: list[dict] = []

    def fetch_all(self, hours: int = 24) -> list[dict]:
        """Fetch stories from all sources published within the last N hours."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        # 1. HackerNews top stories (always reliable)
        hn_stories = self._fetch_hackernews(cutoff, max_stories=15)
        self.all_stories.extend(hn_stories)
        logging.info(f"HackerNews: fetched {len(hn_stories)} stories")

        # 2. ProductHunt (top 5 of the day)
        ph_stories = self._fetch_producthunt()
        self.all_stories.extend(ph_stories)
        logging.info(f"ProductHunt: fetched {len(ph_stories)} products")

        # 3. RSS feeds
        for category, feeds in self.RSS_SOURCES.items():
            for name, url in feeds:
                try:
                    stories = self._fetch_rss(name, url, category, cutoff)
                    self.all_stories.extend(stories)
                    logging.info(f"{name}: fetched {len(stories)} stories")
                except Exception as e:
                    logging.warning(f"Failed to fetch {name}: {e}")

        logging.info(f"Total stories fetched: {len(self.all_stories)}")
        return self.all_stories

    def _fetch_hackernews(self, cutoff: datetime, max_stories: int = 15) -> list[dict]:
        """Fetch top stories from HackerNews API."""
        stories = []
        try:
            req = urllib.request.Request(
                "https://hacker-news.firebaseio.com/v0/topstories.json",
                headers={"User-Agent": "AgentsHub/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                top_ids = json.loads(resp.read().decode())[:30]  # fetch top 30, filter to max_stories

            for story_id in top_ids:
                if len(stories) >= max_stories:
                    break
                try:
                    req = urllib.request.Request(
                        f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                        headers={"User-Agent": "AgentsHub/1.0"}
                    )
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        item = json.loads(resp.read().decode())

                    if not item or item.get("type") != "story":
                        continue

                    story_time = datetime.fromtimestamp(item.get("time", 0), tz=timezone.utc)
                    stories.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                        "source": "HackerNews",
                        "category": "Tech Industry",
                        "score": item.get("score", 0),
                        "comments": item.get("descendants", 0),
                        "published": story_time.isoformat(),
                    })
                except Exception:
                    continue
        except Exception as e:
            logging.warning(f"HackerNews API failed: {e}")
        return stories

    def _fetch_producthunt(self) -> list[dict]:
        """Fetch today's top products from ProductHunt's RSS-like homepage."""
        stories = []
        try:
            # Use the PH RSS feed
            req = urllib.request.Request(
                "https://www.producthunt.com/feed",
                headers={"User-Agent": "AgentsHub/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode("utf-8", errors="replace")

            root = ET.fromstring(content)
            # Try Atom format first, then RSS
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall(".//atom:entry", ns)
            if not entries:
                entries = root.findall(".//item")

            for entry in entries[:5]:
                title = self._xml_text(entry, "atom:title", ns) or self._xml_text(entry, "title")
                link = ""
                link_el = entry.find("atom:link", ns)
                if link_el is not None:
                    link = link_el.get("href", "")
                if not link:
                    link = self._xml_text(entry, "link") or ""

                if title:
                    stories.append({
                        "title": title,
                        "url": link,
                        "source": "ProductHunt",
                        "category": "Startups / Funding",
                        "score": 0,
                        "comments": 0,
                        "published": datetime.now(timezone.utc).isoformat(),
                    })
        except Exception as e:
            logging.warning(f"ProductHunt fetch failed: {e}")
        return stories

    def _fetch_rss(self, name: str, url: str, category: str, cutoff: datetime) -> list[dict]:
        """Parse an RSS/Atom feed and return stories newer than cutoff."""
        stories = []
        req = urllib.request.Request(url, headers={"User-Agent": "AgentsHub/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="replace")

        root = ET.fromstring(content)

        # Handle both RSS and Atom formats
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items = root.findall(".//item")
        if not items:
            items = root.findall(".//atom:entry", ns)

        for item in items[:10]:  # max 10 per feed
            title = self._xml_text(item, "title") or self._xml_text(item, "atom:title", ns)
            link = self._xml_text(item, "link") or ""
            if not link:
                link_el = item.find("atom:link", ns)
                if link_el is not None:
                    link = link_el.get("href", "")

            pub_date_str = (
                self._xml_text(item, "pubDate")
                or self._xml_text(item, "atom:published", ns)
                or self._xml_text(item, "atom:updated", ns)
                or ""
            )

            description = (
                self._xml_text(item, "description")
                or self._xml_text(item, "atom:summary", ns)
                or ""
            )
            # Strip HTML tags from description
            import re
            description = re.sub(r"<[^>]+>", "", description)[:300]

            if title:
                stories.append({
                    "title": title.strip(),
                    "url": link.strip(),
                    "source": name,
                    "category": category,
                    "score": 0,
                    "comments": 0,
                    "published": pub_date_str,
                    "description": description.strip(),
                })

        return stories

    def _xml_text(self, element, tag: str, ns: Optional[dict] = None) -> Optional[str]:
        """Safely extract text from an XML element."""
        el = element.find(tag, ns) if ns else element.find(tag)
        if el is not None and el.text:
            return el.text.strip()
        return None
