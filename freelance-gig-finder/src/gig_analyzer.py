import logging
from google import genai

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class GigAnalyzer:
    """Uses Gemini to rank and summarize freelance gigs into an actionable digest."""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def generate_digest(self, gigs: list[dict], date_str: str) -> str:
        """Generate a ranked gig digest from fetched opportunities."""
        if not gigs:
            return f"# Freelance Gig Finder — {date_str}\n\nNo gigs found today. Sources may be temporarily unavailable."

        gigs_text = ""
        for i, g in enumerate(gigs, 1):
            gigs_text += f"\n---\nGig {i}:\n"
            gigs_text += f"Title: {g.get('title', 'N/A')}\n"
            gigs_text += f"Source: {g.get('source', 'N/A')}\n"
            gigs_text += f"URL: {g.get('url', 'N/A')}\n"
            gigs_text += f"Budget: {g.get('budget', 'Not specified')}\n"
            gigs_text += f"Description: {g.get('description', 'N/A')}\n"

        prompt = f"""You are a freelance gig advisor for a skilled AI/Python developer from India who wants to start an AI business.

His skills: Python, AI agents, LLM integration (Gemini/OpenAI APIs), web scraping, full-stack (React/Node), workflow automation (n8n/Make), chatbot building.

He's looking for gigs he can do as a one-person operation — remote, no full-time commitment.

**YOUR JOB:** From the {len(gigs)} raw gigs below, create a sharp, actionable daily digest.

**RULES:**
1. Pick the **top 10-15 best gigs** — high pay, clear scope, matches his skills. Drop garbage/spam/unclear gigs.
2. Rank them: 🔥 Hot (high pay + perfect skill match), ⭐ Good (solid opportunity), 📌 Worth a Look.
3. For each gig, write:
   - **Title** (cleaned up, not the raw spam title)
   - Budget/Rate (if available)
   - One line: what they actually need
   - Platform + direct link
4. Group by category: 🤖 AI & Automation, 🐍 Python & Backend, 🌐 Full Stack, 🔧 Other
5. End with a "💡 Market Signal" section: What patterns do you see in today's gigs? What's hot? What should he consider productizing?
6. Keep it scannable. No fluff.

**FORMAT:**
```
# 💼 Freelance Gig Digest — {date_str}

## 🔥 Hot Opportunities
- **Title** — Budget: $X | What they need in one line | [Platform](url)
- ...

## ⭐ Good Matches
- ...

## 📌 Worth a Look
- ...

---

## 💡 Market Signal
2-3 sentences on patterns...
```

**RAW GIGS:**
{gigs_text}
"""
        logging.info("Calling Gemini API to analyze gigs...")
        response = self.client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt,
        )

        if response and response.text:
            return response.text
        else:
            return f"# Freelance Gig Digest — {date_str}\n\nFailed to generate digest. Gemini API returned empty response."
