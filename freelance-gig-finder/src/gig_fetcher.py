import json
import logging
import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class GigFetcher:
    """Fetches freelance gigs from multiple free platforms."""

    HEADERS = {"User-Agent": "AgentsHub/1.0 (Job Search Agent)"}

    def __init__(self, keywords: list[str]):
        self.keywords = keywords
        self.all_gigs: list[dict] = []

    def fetch_all(self) -> list[dict]:
        """Fetch gigs from all available sources."""

        # 1. Upwork RSS feeds (most reliable)
        upwork_gigs = self._fetch_upwork_rss()
        self.all_gigs.extend(upwork_gigs)
        logging.info(f"Upwork: fetched {len(upwork_gigs)} gigs")

        # 2. RemoteOK API (free, no key)
        remoteok_gigs = self._fetch_remoteok()
        self.all_gigs.extend(remoteok_gigs)
        logging.info(f"RemoteOK: fetched {len(remoteok_gigs)} gigs")

        # 3. Freelancer RSS
        freelancer_gigs = self._fetch_freelancer_rss()
        self.all_gigs.extend(freelancer_gigs)
        logging.info(f"Freelancer: fetched {len(freelancer_gigs)} gigs")

        # 4. HackerNews "Who is Hiring" (monthly, valuable leads)
        hn_gigs = self._fetch_hn_hiring()
        self.all_gigs.extend(hn_gigs)
        logging.info(f"HN Hiring: fetched {len(hn_gigs)} gigs")

        # Deduplicate by title similarity
        self.all_gigs = self._deduplicate(self.all_gigs)
        logging.info(f"Total unique gigs: {len(self.all_gigs)}")
        return self.all_gigs

    def _fetch_upwork_rss(self) -> list[dict]:
        """Fetch from Upwork RSS feeds for each keyword group."""
        gigs = []
        # Upwork RSS feed URL pattern
        search_queries = [
            "AI agent developer",
            "LLM chatbot Python",
            "AI automation",
            "web scraping Python",
            "workflow automation n8n",
            "full stack React Node",
        ]

        for query in search_queries:
            try:
                encoded = urllib.parse.quote(query)
                url = f"https://www.upwork.com/ab/feed/jobs/rss?q={encoded}&sort=recency"
                req = urllib.request.Request(url, headers=self.HEADERS)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    content = resp.read().decode("utf-8", errors="replace")

                root = ET.fromstring(content)
                items = root.findall(".//item")

                for item in items[:5]:  # top 5 per query
                    title = self._xml_text(item, "title") or ""
                    link = self._xml_text(item, "link") or ""
                    description = self._xml_text(item, "description") or ""
                    pub_date = self._xml_text(item, "pubDate") or ""

                    # Strip HTML from description
                    import re
                    clean_desc = re.sub(r"<[^>]+>", "", description)[:500]

                    # Extract budget if present
                    budget = ""
                    budget_match = re.search(r"Budget[:\s]*\$?([\d,]+(?:\s*-\s*\$?[\d,]+)?)", clean_desc, re.IGNORECASE)
                    if budget_match:
                        budget = f"${budget_match.group(1)}"
                    hourly_match = re.search(r"Hourly Range[:\s]*\$?([\d.]+-\$?[\d.]+)", clean_desc, re.IGNORECASE)
                    if hourly_match:
                        budget = f"${hourly_match.group(1)}/hr"

                    if title:
                        gigs.append({
                            "title": title.strip(),
                            "url": link.strip(),
                            "source": "Upwork",
                            "description": clean_desc[:300],
                            "budget": budget,
                            "published": pub_date,
                            "search_query": query,
                        })
            except Exception as e:
                logging.warning(f"Upwork RSS failed for '{query}': {e}")
        return gigs

    def _fetch_remoteok(self) -> list[dict]:
        """Fetch from RemoteOK API (free, JSON)."""
        gigs = []
        try:
            req = urllib.request.Request(
                "https://remoteok.com/api",
                headers={**self.HEADERS, "Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            # First element is legal notice, skip it
            jobs = data[1:] if len(data) > 1 else []

            # Filter by relevance to our keywords
            keyword_lower = [k.lower() for k in self.keywords]
            cutoff = datetime.now(timezone.utc) - timedelta(hours=48)

            for job in jobs:
                title = job.get("position", "")
                company = job.get("company", "")
                tags = [t.lower() for t in job.get("tags", [])]
                description = job.get("description", "")[:300]
                url = job.get("url", "")
                date_str = job.get("date", "")
                salary = ""
                if job.get("salary_min") and job.get("salary_max"):
                    salary = f"${job['salary_min']:,}-${job['salary_max']:,}/yr"

                # Check relevance
                searchable = f"{title} {' '.join(tags)} {description}".lower()
                is_relevant = any(kw in searchable for kw in keyword_lower)

                if is_relevant and title:
                    gigs.append({
                        "title": f"{title} at {company}" if company else title,
                        "url": f"https://remoteok.com{url}" if url.startswith("/") else url,
                        "source": "RemoteOK",
                        "description": description[:300],
                        "budget": salary,
                        "published": date_str,
                        "search_query": "remote",
                    })

                if len(gigs) >= 10:
                    break
        except Exception as e:
            logging.warning(f"RemoteOK API failed: {e}")
        return gigs

    def _fetch_freelancer_rss(self) -> list[dict]:
        """Fetch from Freelancer.com RSS feeds."""
        gigs = []
        queries = ["python+ai", "chatbot+llm", "web+scraping", "automation"]

        for query in queries:
            try:
                url = f"https://www.freelancer.com/rss.xml?keyword={query}&min_price=100"
                req = urllib.request.Request(url, headers=self.HEADERS)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    content = resp.read().decode("utf-8", errors="replace")

                root = ET.fromstring(content)
                items = root.findall(".//item")

                for item in items[:5]:
                    title = self._xml_text(item, "title") or ""
                    link = self._xml_text(item, "link") or ""
                    description = self._xml_text(item, "description") or ""

                    import re
                    clean_desc = re.sub(r"<[^>]+>", "", description)[:300]

                    budget = ""
                    budget_match = re.search(r"\$(\d[\d,]*)", clean_desc)
                    if budget_match:
                        budget = f"${budget_match.group(1)}"

                    if title:
                        gigs.append({
                            "title": title.strip(),
                            "url": link.strip(),
                            "source": "Freelancer",
                            "description": clean_desc[:300],
                            "budget": budget,
                            "published": self._xml_text(item, "pubDate") or "",
                            "search_query": query,
                        })
            except Exception as e:
                logging.warning(f"Freelancer RSS failed for '{query}': {e}")
        return gigs

    def _fetch_hn_hiring(self) -> list[dict]:
        """Search HackerNews 'Who is Hiring' threads for relevant gigs."""
        gigs = []
        try:
            # Search for the latest "Who is Hiring" thread
            search_url = "https://hn.algolia.com/api/v1/search?query=who+is+hiring&tags=ask_hn&hitsPerPage=1"
            req = urllib.request.Request(search_url, headers=self.HEADERS)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            hits = data.get("hits", [])
            if not hits:
                return gigs

            thread_id = hits[0].get("objectID")
            if not thread_id:
                return gigs

            # Fetch comments from the thread
            comments_url = f"https://hn.algolia.com/api/v1/items/{thread_id}"
            req = urllib.request.Request(comments_url, headers=self.HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                thread = json.loads(resp.read().decode())

            children = thread.get("children", [])
            keyword_lower = [k.lower() for k in self.keywords]

            for comment in children[:100]:  # Check first 100 comments
                text = comment.get("text", "")
                if not text:
                    continue

                text_lower = text.lower()
                is_relevant = any(kw in text_lower for kw in keyword_lower)

                if is_relevant:
                    import re
                    clean_text = re.sub(r"<[^>]+>", "", text)[:400]
                    # Try to extract company name (usually first line)
                    first_line = clean_text.split("\n")[0][:100] if clean_text else "HN Job Posting"

                    gigs.append({
                        "title": first_line,
                        "url": f"https://news.ycombinator.com/item?id={comment.get('id', thread_id)}",
                        "source": "HN Who's Hiring",
                        "description": clean_text[:300],
                        "budget": "",
                        "published": comment.get("created_at", ""),
                        "search_query": "hn_hiring",
                    })

                if len(gigs) >= 10:
                    break
        except Exception as e:
            logging.warning(f"HN Hiring fetch failed: {e}")
        return gigs

    def _deduplicate(self, gigs: list[dict]) -> list[dict]:
        """Remove duplicate gigs by normalized title."""
        seen = set()
        unique = []
        for gig in gigs:
            key = gig["title"].lower().strip()[:60]
            if key not in seen:
                seen.add(key)
                unique.append(gig)
        return unique

    def _xml_text(self, element, tag: str) -> Optional[str]:
        el = element.find(tag)
        if el is not None and el.text:
            return el.text.strip()
        return None
