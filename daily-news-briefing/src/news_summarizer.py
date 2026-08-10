import logging
from google import genai

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class NewsSummarizer:
    """Uses Gemini to create a curated daily briefing from raw news stories."""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def generate_briefing(self, stories: list[dict], date_str: str) -> str:
        """Generate a markdown news briefing from fetched stories."""
        if not stories:
            return f"# Daily Tech Briefing — {date_str}\n\nNo stories found today. Sources may be temporarily unavailable."

        # Build raw stories context
        stories_text = ""
        for i, s in enumerate(stories, 1):
            stories_text += f"\n---\nStory {i}:\n"
            stories_text += f"Title: {s.get('title', 'N/A')}\n"
            stories_text += f"Source: {s.get('source', 'N/A')} ({s.get('category', 'N/A')})\n"
            stories_text += f"URL: {s.get('url', 'N/A')}\n"
            if s.get("score"):
                stories_text += f"Score/Upvotes: {s['score']}\n"
            if s.get("comments"):
                stories_text += f"Comments: {s['comments']}\n"
            if s.get("description"):
                stories_text += f"Description: {s['description'][:200]}\n"

        prompt = f"""You are a personal tech news curator for a 22-year-old ambitious CS student and aspiring AI entrepreneur from India.

Your job: Turn this raw list of {len(stories)} stories into a sharp, scannable daily briefing he can read in 2 minutes flat.

**RULES:**
1. Pick the **top 10-12 most important/interesting stories** from the list. Skip duplicates, fluff, and generic press releases.
2. Group them by category: 🤖 AI & ML, 🚀 Startups & Funding, 🇮🇳 Indian Tech, 💻 Tech Industry, 🛠️ Product Launches
3. For each story, write exactly:
   - **One-line headline** (bold, punchy, no filler)
   - One sentence on why it matters (insight, not summary)
   - The source link
4. At the end, add a "⚡ Quick Take" section: 2-3 sentences on the overall theme of today's news and what it means for someone building an AI business.
5. Use clean markdown formatting. Keep it tight — no fluff, no filler, no "Good morning!" crap.

**FORMAT:**
```
# 📰 Daily Tech Briefing — {date_str}

## 🤖 AI & ML
- **Headline here** — Why it matters. [Source](url)
- ...

## 🚀 Startups & Funding
- ...

## 🇮🇳 Indian Tech
- ...

## 💻 Tech Industry
- ...

## 🛠️ Product Launches
- ...

---

## ⚡ Quick Take
2-3 sentences...
```

**RAW STORIES:**
{stories_text}
"""
        logging.info("Calling Gemini API to generate news briefing...")
        response = self.client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt,
        )

        if response and response.text:
            return response.text
        else:
            return f"# Daily Tech Briefing — {date_str}\n\nFailed to generate briefing. Gemini API returned empty response."
