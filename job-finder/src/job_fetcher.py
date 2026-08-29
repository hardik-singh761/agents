import json
import re
import logging
import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class JobFetcher:
    """Fetches AI/ML/Data Science job listings from India-focused free sources."""

    HEADERS = {"User-Agent": "AgentsHub/1.0 (Job Finder Agent)"}

    def __init__(self, search_keywords: list[str], experience_keywords: list[str],
                 target_companies: list[str], locations: list[str]):
        self.search_keywords = [k.lower() for k in search_keywords]
        self.experience_keywords = [k.lower() for k in experience_keywords]
        self.target_companies = [c.lower() for c in target_companies]
        self.locations = locations
        self.all_jobs: list[dict] = []

    def fetch_all(self) -> list[dict]:
        """Fetch jobs from all available India-focused sources."""

        # 1. ai-jobs.net RSS — THE best AI/ML job board
        aijobs = self._fetch_aijobs_rss()
        self.all_jobs.extend(aijobs)
        logging.info(f"AI-Jobs.net: fetched {len(aijobs)} jobs")

        # 2. Greenhouse ATS — direct from big company career pages
        greenhouse = self._fetch_greenhouse_jobs()
        self.all_jobs.extend(greenhouse)
        logging.info(f"Greenhouse (company career pages): fetched {len(greenhouse)} jobs")

        # 3. Lever ATS — direct from company career pages
        lever = self._fetch_lever_jobs()
        self.all_jobs.extend(lever)
        logging.info(f"Lever (company career pages): fetched {len(lever)} jobs")

        # 4. Jobicy API — remote/India jobs
        jobicy = self._fetch_jobicy()
        self.all_jobs.extend(jobicy)
        logging.info(f"Jobicy: fetched {len(jobicy)} jobs")

        # 5. Himalayas RSS — remote jobs filtered for AI/ML
        himalayas = self._fetch_himalayas()
        self.all_jobs.extend(himalayas)
        logging.info(f"Himalayas: fetched {len(himalayas)} jobs")

        # 6. HN Who's Hiring — filtered for India/Remote
        hn = self._fetch_hn_hiring()
        self.all_jobs.extend(hn)
        logging.info(f"HN Who's Hiring: fetched {len(hn)} jobs")

        # 7. Arbeitnow — with location filter
        arbeitnow = self._fetch_arbeitnow()
        self.all_jobs.extend(arbeitnow)
        logging.info(f"Arbeitnow: fetched {len(arbeitnow)} jobs")

        # 8. LinkedIn via Google Search
        linkedin = self._fetch_linkedin_via_google()
        self.all_jobs.extend(linkedin)
        logging.info(f"LinkedIn/Google: fetched {len(linkedin)} jobs")

        # Hard filter out senior/staff/lead roles from the title
        fresher_jobs = []
        senior_terms = ["senior", "sr.", "sr ", "staff", "principal", "lead", "director", "manager", "head of", "vp ", "architect", "founding", "experienced"]
        for job in self.all_jobs:
            title_lower = job.get("title", "").lower()
            if not any(term in title_lower for term in senior_terms):
                fresher_jobs.append(job)

        # Deduplicate
        self.all_jobs = self._deduplicate(fresher_jobs)
        logging.info(f"Total unique fresher-friendly jobs after dedup: {len(self.all_jobs)}")
        return self.all_jobs

    def _is_relevant(self, text: str) -> bool:
        """Check if text matches our target AI/ML/DS keywords."""
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.search_keywords)

    def _is_india_or_remote(self, location: str) -> bool:
        """Check if the job location is in India or Remote."""
        loc_lower = location.lower()
        india_terms = [
            "india", "bangalore", "bengaluru", "hyderabad", "pune", "mumbai",
            "delhi", "gurgaon", "gurugram", "noida", "chennai", "kolkata",
            "ahmedabad", "jaipur", "kochi", "coimbatore", "indore",
            "remote", "anywhere", "worldwide", "global",
        ]
        return any(term in loc_lower for term in india_terms)

    def _is_big_company(self, company: str) -> bool:
        company_lower = company.lower()
        return any(tc in company_lower for tc in self.target_companies)

    def _experience_score(self, text: str) -> int:
        text_lower = text.lower()
        score = 0
        for kw in self.experience_keywords:
            if kw in text_lower:
                score += 1
        senior_terms = ["senior", "staff", "principal", "lead", "director", "manager",
                        "head of", "vp ", "5+ year", "7+ year", "10+ year"]
        for term in senior_terms:
            if term in text_lower:
                score -= 2
        return score

    # ─── Source 1: ai-jobs.net RSS ───────────────────────────────

    def _fetch_aijobs_rss(self) -> list[dict]:
        """Fetch from ai-jobs.net RSS — dedicated AI/ML job board."""
        jobs = []
        try:
            req = urllib.request.Request("https://ai-jobs.net/feed/", headers=self.HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8", errors="replace")

            root = ET.fromstring(content)
            items = root.findall(".//item")

            for item in items:
                title = self._xml_text(item, "title") or ""
                link = self._xml_text(item, "link") or ""
                description = self._xml_text(item, "description") or ""
                pub_date = self._xml_text(item, "pubDate") or ""

                clean_desc = re.sub(r"<[^>]+>", "", description)[:500]

                # Extract company and location from description or title
                company = ""
                location = ""

                # ai-jobs.net often has "Company — Location" in the description
                company_match = re.search(r"(?:at|@|company[:\s]+)\s*([^\n,|]+)", clean_desc, re.IGNORECASE)
                if company_match:
                    company = company_match.group(1).strip()[:60]

                # Check for India/Remote location
                loc_match = re.search(
                    r"(?:India|Bangalore|Bengaluru|Hyderabad|Pune|Mumbai|Delhi|"
                    r"Gurgaon|Gurugram|Noida|Chennai|Remote|Worldwide|Global|"
                    r"Anywhere|Kolkata|Ahmedabad|Kochi)",
                    f"{title} {clean_desc}", re.IGNORECASE
                )
                if loc_match:
                    location = loc_match.group(0)

                searchable = f"{title} {clean_desc}"
                if self._is_relevant(searchable) and (location or self._is_relevant(title)):
                    jobs.append({
                        "title": title.strip(),
                        "company": company,
                        "url": link.strip(),
                        "source": "AI-Jobs.net",
                        "location": location or "Check listing",
                        "salary": "",
                        "description": clean_desc[:400],
                        "published": pub_date,
                        "is_big_company": self._is_big_company(company),
                        "experience_score": self._experience_score(f"{title} {clean_desc}"),
                    })
        except Exception as e:
            logging.warning(f"AI-Jobs.net RSS failed: {e}")
        return jobs

    # ─── Source 2: Greenhouse ATS (big companies) ────────────────

    # These are real company career page slugs — free, public, legal API
    GREENHOUSE_COMPANIES = {
        # Valid Indian/Global companies that use Greenhouse and have active jobs
        "groww": "Groww",
        "slice": "Slice",
        "postman": "Postman",
        "figma": "Figma",
        "twilio": "Twilio",
        "stripe": "Stripe",
        "airbnb": "Airbnb",
        "gitlab": "GitLab",
        "elastic": "Elastic",
        "cockroachlabs": "Cockroach Labs",
        "mongodb": "MongoDB",
        "pagerduty": "PagerDuty",
        "okta": "Okta",
        "zscaler": "Zscaler",
        "samsara": "Samsara",
        "rubrik": "Rubrik"
    }

    def _fetch_greenhouse_jobs(self) -> list[dict]:
        """Fetch from Greenhouse boards API — direct career pages of big companies."""
        jobs = []
        for slug, company_name in self.GREENHOUSE_COMPANIES.items():
            try:
                url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
                req = urllib.request.Request(url, headers=self.HEADERS)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())

                for job in data.get("jobs", []):
                    title = job.get("title", "")
                    job_url = job.get("absolute_url", "")
                    location_name = job.get("location", {}).get("name", "")
                    updated = job.get("updated_at", "")

                    # Only include if role is relevant AND location is India/Remote
                    if self._is_relevant(title) and self._is_india_or_remote(location_name):
                        jobs.append({
                            "title": title.strip(),
                            "company": company_name,
                            "url": job_url,
                            "source": f"Greenhouse ({company_name})",
                            "location": location_name,
                            "salary": "",
                            "description": f"Direct from {company_name} career page",
                            "published": updated[:10] if updated else "",
                            "is_big_company": True,
                            "experience_score": self._experience_score(title),
                        })
            except Exception as e:
                logging.warning(f"Greenhouse failed for {company_name} ({slug}): {e}")
        return jobs

    # ─── Source 3: Lever ATS (big companies) ─────────────────────

    LEVER_COMPANIES = {
        # Valid companies that use Lever and have active jobs
        "freshworks": "Freshworks",
        "fi": "Fi",
        "palantir": "Palantir"
    }

    def _fetch_lever_jobs(self) -> list[dict]:
        """Fetch from Lever postings API — direct from company career pages."""
        jobs = []
        for slug, company_name in self.LEVER_COMPANIES.items():
            try:
                url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
                req = urllib.request.Request(url, headers=self.HEADERS)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())

                for job in data:
                    title = job.get("text", "")
                    job_url = job.get("hostedUrl", "") or job.get("applyUrl", "")
                    categories = job.get("categories", {})
                    location_name = categories.get("location", "") or categories.get("allLocations", [""])[0] if isinstance(categories.get("allLocations"), list) else ""
                    team = categories.get("team", "")
                    created = job.get("createdAt", 0)

                    # Convert timestamp
                    pub_date = ""
                    if created:
                        try:
                            pub_date = datetime.fromtimestamp(created / 1000).strftime("%Y-%m-%d")
                        except Exception:
                            pass

                    if self._is_relevant(f"{title} {team}") and self._is_india_or_remote(str(location_name)):
                        jobs.append({
                            "title": title.strip(),
                            "company": company_name,
                            "url": job_url,
                            "source": f"Lever ({company_name})",
                            "location": str(location_name),
                            "salary": "",
                            "description": f"Team: {team}. Direct from {company_name} career page",
                            "published": pub_date,
                            "is_big_company": True,
                            "experience_score": self._experience_score(title),
                        })
            except Exception as e:
                logging.warning(f"Lever failed for {company_name} ({slug}): {e}")
        return jobs

    # ─── Source 4: Jobicy API ────────────────────────────────────

    def _fetch_jobicy(self) -> list[dict]:
        """Fetch from Jobicy free API — remote jobs."""
        jobs = []
        tags = ["ai", "machine-learning", "data-science", "python"]
        for tag in tags:
            try:
                url = f"https://jobicy.com/api/v2/remote-jobs?count=20&tag={tag}"
                req = urllib.request.Request(url, headers=self.HEADERS)
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode())

                for job in data.get("jobs", []):
                    title = job.get("jobTitle", "")
                    company = job.get("companyName", "")
                    job_url = job.get("url", "")
                    location = job.get("jobGeo", "Remote")
                    job_type = job.get("jobType", "")
                    pub_date = job.get("pubDate", "")

                    # Only include India-relevant or remote/worldwide
                    if self._is_relevant(title) and self._is_india_or_remote(location):
                        jobs.append({
                            "title": title.strip(),
                            "company": company.strip(),
                            "url": job_url,
                            "source": "Jobicy",
                            "location": location,
                            "salary": "",
                            "description": f"Type: {job_type}",
                            "published": pub_date,
                            "is_big_company": self._is_big_company(company),
                            "experience_score": self._experience_score(title),
                        })
            except Exception as e:
                logging.warning(f"Jobicy failed for tag '{tag}': {e}")
        return jobs

    # ─── Source 5: Himalayas RSS ─────────────────────────────────

    def _fetch_himalayas(self) -> list[dict]:
        """Fetch from Himalayas RSS feed — remote jobs."""
        jobs = []
        try:
            req = urllib.request.Request("https://himalayas.app/jobs/rss", headers=self.HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8", errors="replace")

            root = ET.fromstring(content)
            items = root.findall(".//item")

            for item in items:
                title = self._xml_text(item, "title") or ""
                link = self._xml_text(item, "link") or ""
                description = self._xml_text(item, "description") or ""
                pub_date = self._xml_text(item, "pubDate") or ""

                clean_desc = re.sub(r"<[^>]+>", "", description)[:500]

                company = ""
                if " at " in title:
                    parts = title.rsplit(" at ", 1)
                    company = parts[1].strip() if len(parts) == 2 else ""

                searchable = f"{title} {clean_desc}"
                if self._is_relevant(searchable):
                    jobs.append({
                        "title": title.strip(),
                        "company": company,
                        "url": link.strip(),
                        "source": "Himalayas",
                        "location": "Remote (Worldwide)",
                        "salary": "",
                        "description": clean_desc[:400],
                        "published": pub_date,
                        "is_big_company": self._is_big_company(company),
                        "experience_score": self._experience_score(f"{title} {clean_desc}"),
                    })
        except Exception as e:
            logging.warning(f"Himalayas RSS failed: {e}")
        return jobs

    # ─── Source 6: HN Who's Hiring (India-filtered) ──────────────

    def _fetch_hn_hiring(self) -> list[dict]:
        """Search HN 'Who is Hiring' threads — filter for India/Remote mentions."""
        jobs = []
        try:
            search_url = "https://hn.algolia.com/api/v1/search?query=who+is+hiring&tags=ask_hn&hitsPerPage=1"
            req = urllib.request.Request(search_url, headers=self.HEADERS)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            hits = data.get("hits", [])
            if not hits:
                return jobs

            thread_id = hits[0].get("objectID")
            if not thread_id:
                return jobs

            comments_url = f"https://hn.algolia.com/api/v1/items/{thread_id}"
            req = urllib.request.Request(comments_url, headers=self.HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                thread = json.loads(resp.read().decode())

            children = thread.get("children", [])

            for comment in children[:200]:
                text = comment.get("text", "")
                if not text:
                    continue

                # Only include if mentions India or Remote AND is AI/ML relevant
                if self._is_relevant(text) and self._is_india_or_remote(text):
                    clean_text = re.sub(r"<[^>]+>", "", text)[:500]
                    first_line = clean_text.split("\n")[0][:120] if clean_text else "HN Job Posting"

                    company = first_line.split("|")[0].strip() if "|" in first_line else first_line[:60]

                    location = "Remote"
                    india_cities = ["India", "Bangalore", "Bengaluru", "Hyderabad", "Pune", "Mumbai", "Delhi", "Gurgaon", "Noida", "Chennai"]
                    for city in india_cities:
                        if city.lower() in text.lower():
                            location = city
                            break

                    jobs.append({
                        "title": first_line[:100],
                        "company": company,
                        "url": f"https://news.ycombinator.com/item?id={comment.get('id', thread_id)}",
                        "source": "HN Who's Hiring",
                        "location": location,
                        "salary": "",
                        "description": clean_text[:400],
                        "published": comment.get("created_at", ""),
                        "is_big_company": self._is_big_company(company),
                        "experience_score": self._experience_score(clean_text),
                    })

                if len(jobs) >= 15:
                    break
        except Exception as e:
            logging.warning(f"HN Hiring failed: {e}")
        return jobs

    # ─── Source 7: Arbeitnow API ─────────────────────────────────

    def _fetch_arbeitnow(self) -> list[dict]:
        """Fetch from Arbeitnow free JSON API."""
        jobs = []
        search_terms = ["machine+learning", "ai+engineer", "data+scientist", "generative+ai"]

        for term in search_terms:
            try:
                url = f"https://www.arbeitnow.com/api/job-board-api?search={term}"
                req = urllib.request.Request(url, headers=self.HEADERS)
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode())

                for job in data.get("data", [])[:10]:
                    title = job.get("title", "")
                    company = job.get("company_name", "")
                    job_url = job.get("url", "")
                    location = job.get("location", "")
                    description = job.get("description", "")[:500]
                    tags = ", ".join(job.get("tags", []))
                    remote = job.get("remote", False)
                    created = job.get("created_at", "")

                    clean_desc = re.sub(r"<[^>]+>", "", description)[:400]

                    loc_str = f"{location}{' (Remote)' if remote else ''}"

                    # Only include India/Remote
                    if self._is_relevant(f"{title} {tags} {clean_desc}") and self._is_india_or_remote(loc_str):
                        jobs.append({
                            "title": title.strip(),
                            "company": company.strip(),
                            "url": job_url.strip(),
                            "source": "Arbeitnow",
                            "location": loc_str,
                            "salary": "",
                            "description": clean_desc,
                            "published": str(created),
                            "is_big_company": self._is_big_company(company),
                            "experience_score": self._experience_score(f"{title} {clean_desc}"),
                        })
            except Exception as e:
                logging.warning(f"Arbeitnow failed for '{term}': {e}")
        return jobs

    # ─── Source 8: LinkedIn via Google Search ────────────────────

    def _fetch_linkedin_via_google(self) -> list[dict]:
        """Use Google Search to find recent LinkedIn job postings for India."""
        jobs = []
        # Target AI roles in major Indian tech hubs
        queries = [
            "site:in.linkedin.com/jobs/view/ \"AI Engineer\" OR \"Machine Learning\" Bangalore OR Hyderabad OR Pune",
            "site:in.linkedin.com/jobs/view/ \"Data Scientist\" OR \"GenAI\" India fresher OR \"entry level\""
        ]
        
        for q in queries:
            try:
                url = "https://www.google.com/search?q=" + urllib.parse.quote(q) + "&tbs=qdr:w" # Past week only
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                })
                with urllib.request.urlopen(req, timeout=10) as resp:
                    html = resp.read().decode("utf-8", errors="ignore")
                
                # Extract LinkedIn URLs and Titles
                links = re.findall(r'href="(https://in\.linkedin\.com/jobs/view/[^"]+)"', html)
                
                for link in set(links):
                    # Basic extraction from URL slug
                    parts = link.split("/")[-1].split("-")
                    title_parts = [p for p in parts if not p.isdigit() and p not in ["at", "in", "job"]]
                    title = " ".join(title_parts).title().replace("Machine Learning", "ML")
                    
                    if self._is_relevant(title):
                        jobs.append({
                            "title": title[:100],
                            "company": "See LinkedIn",
                            "url": link,
                            "source": "LinkedIn (via Google)",
                            "location": "India",
                            "salary": "",
                            "description": "LinkedIn Job Posting. Click to view details.",
                            "published": "Recent",
                            "is_big_company": False,
                            "experience_score": 0,
                        })
            except Exception as e:
                logging.warning(f"LinkedIn/Google search failed for query: {e}")
                
        return jobs

    # ─── Utilities ───────────────────────────────────────────────

    def _deduplicate(self, jobs: list[dict]) -> list[dict]:
        seen = set()
        unique = []
        for job in jobs:
            key = f"{job['title'].lower().strip()[:50]}|{job.get('company', '').lower().strip()[:30]}"
            if key not in seen:
                seen.add(key)
                unique.append(job)
        return unique

    def _xml_text(self, element, tag: str) -> Optional[str]:
        el = element.find(tag)
        if el is not None and el.text:
            return el.text.strip()
        return None
