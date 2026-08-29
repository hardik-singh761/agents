import logging
from google import genai

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class JobAnalyzer:
    """Uses Gemini to rank and format job listings into an actionable daily digest."""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def generate_digest(self, jobs: list[dict], date_str: str) -> str:
        """Generate a ranked job digest from fetched listings."""
        if not jobs:
            return f"""# 🎯 Daily Job Finder — {date_str}

No matching AI/ML/Data Science jobs found today across any source.
The agent checked RemoteOK, Himalayas, Remotive, Arbeitnow, HN Who's Hiring, WorkAnywhere, and LinkedIn.

This can happen if sources are temporarily down. The agent will try again tomorrow.
"""

        jobs_text = ""
        for i, j in enumerate(jobs, 1):
            jobs_text += f"\n---\nJob {i}:\n"
            jobs_text += f"Title: {j.get('title', 'N/A')}\n"
            jobs_text += f"Company: {j.get('company', 'Not specified')}\n"
            jobs_text += f"Location: {j.get('location', 'Not specified')}\n"
            jobs_text += f"Source: {j.get('source', 'N/A')}\n"
            jobs_text += f"URL: {j.get('url', 'N/A')}\n"
            jobs_text += f"Salary: {j.get('salary', 'Not specified')}\n"
            jobs_text += f"Big Company: {'Yes' if j.get('is_big_company') else 'No'}\n"
            jobs_text += f"Experience Score: {j.get('experience_score', 0)}\n"
            jobs_text += f"Description: {j.get('description', 'N/A')}\n"

        prompt = f"""You are a job search advisor for Hardik Singh, a fresher AI engineer based in India.

**ABOUT HARDIK:**
- Recent graduate with 2 months internship experience at Dell Technologies
- Skills: Python, AI/ML, LLMs, Generative AI, Agentic AI, Data Science, Deep Learning, NLP
- Looking for: AI Engineer, GenAI Engineer, Agentic AI, Data Scientist, ML Engineer roles
- Experience level: Fresher / Entry-level (0-2 years)
- **LOCATION PRIORITY: INDIA ONLY.** He wants jobs in Indian cities (Bangalore, Hyderabad, Pune, Mumbai, Delhi NCR, Chennai) or Remote roles that explicitly accept India-based candidates.
- **EXCLUDE** jobs that are only available in the US, Europe, or other countries unless they clearly state "Remote - India OK" or have an India office.

**YOUR JOB:** From the {len(jobs)} raw job listings below, create a **sharp, actionable daily job digest** he can use to apply immediately.

**STRICT RULES:**
1. **PRIORITIZE** roles that match his experience level (fresher/junior/entry-level/0-2 years). Mark senior roles clearly.
2. **RANK** by relevance: Best matches first. Prioritize big/known companies.
3. For EACH job, output:
   - **Job Title** (cleaned up)
   - **Company Name**
   - **Location** (City, Remote, Hybrid)
   - **Why Apply** — 1 line on why this is a good fit for Hardik
   - **⚠️ Note** — if the role looks senior or may not be fresher-friendly, say so
   - **🔗 Apply Link** — direct clickable URL
4. Group jobs into:
   - 🔥 **Best Matches** (fresher-friendly + good company + relevant role)
   - ⭐ **Worth Applying** (relevant role, may need slight stretch)
   - 📌 **Keep on Radar** (senior roles at great companies — worth a shot anyway)
5. At the end, add a **📊 Market Snapshot** section:
   - Which roles are most in demand today?
   - Any patterns in company hiring?
   - Quick strategic advice for Hardik's job search
6. Keep the formatting ultra-clean. This goes straight to email.
7. EVERY job MUST have the direct apply link. No exceptions.

**FORMAT:**
```
# 🎯 Daily Job Finder — {date_str}
**Jobs Found:** X | **Sources:** RemoteOK, Himalayas, Remotive, Arbeitnow, HN, LinkedIn

---

## 🔥 Best Matches (Apply Today!)

### 1. Job Title
- **Company:** Company Name
- **Location:** City / Remote
- **Why Apply:** One line reason
- **🔗 [Apply Here](url)**

### 2. ...

---

## ⭐ Worth Applying

### 3. ...

---

## 📌 Keep on Radar

### 4. ...

---

## 📊 Market Snapshot
- Demand trends...
- Strategic advice...
```

**RAW JOB LISTINGS:**
{jobs_text}
"""
        logging.info("Calling Gemini API to analyze and rank jobs...")
        response = self.client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt,
        )

        if response and response.text:
            return response.text
        else:
            return f"# 🎯 Daily Job Finder — {date_str}\n\nFailed to generate digest. Gemini API returned empty response."
