import logging
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class EmailSummarizerAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def generate_summary(self, email_list: list[dict], target_email: str, report_date_str: str) -> str:
        """
        Generates a structured Markdown daily summary of the fetched emails using Gemini AI.
        """
        if not email_list:
            return f"""# 📬 Daily Email Digest - {report_date_str}
**Target Inbox:** `{target_email}`  
**Period:** Last 24 Hours  

---

### 🟢 Status: All Clear!
No emails were received in the last 24-hour period.

---
*Generated automatically by your Daily Email Summarizer Agent at 08:00 AM.*
"""

        if not self.client:
            logging.warning("GEMINI_API_KEY not found. Generating basic fallback report without AI summarization.")
            return self._generate_fallback_summary(email_list, target_email, report_date_str)

        prompt = f"""
You are an executive personal assistant AI agent.
Below is the list of emails received in the last 24 hours for `{target_email}`.
Your job is to read all these emails and produce a clean, highly structured, executive-ready Daily Morning Digest in GitHub-Flavored Markdown.

Date: {report_date_str}
Total Emails Received: {len(email_list)}

EMAILED DATA:
"""
        for idx, email_item in enumerate(email_list, 1):
            prompt += f"""
--- Email #{idx} ---
From: {email_item['sender']}
Subject: {email_item['subject']}
Date: {email_item['date']}
Content:
{email_item['body_snippet']}
"""

        prompt += """

REQUIREMENTS FOR THE MARKDOWN OUTPUT:
1. Header: `# 📬 Daily Email Digest - [Date]` with metadata (Total emails count, Target inbox).
2. **🚨 Action Required / High Priority**: Highlight emails that require immediate response, action items, or critical updates. If none, state "None".
3. **📊 Executive Summary**: A bulleted breakdown of key themes, topics, and updates across all emails.
4. **📋 Complete Emails Overview Table**: A GFM table with columns:
   | # | Time | From | Subject | Category / Priority | 1-Line Summary |
5. Use callouts (`> [!NOTE]`, `> [!IMPORTANT]`, `> [!WARNING]`) for key highlights where appropriate.
6. Keep the formatting ultra-clean, readable, and easy to skim in 60 seconds every morning.
"""

        try:
            logging.info("Calling Gemini API to generate daily email summary...")
            response = self.client.models.generate_content(
                model='gemini-flash-lite-latest',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=3000,
                )
            )
            return response.text
        except Exception as e:
            logging.error(f"Error calling Gemini API: {e}")
            return self._generate_fallback_summary(email_list, target_email, report_date_str)

    def _generate_fallback_summary(self, email_list: list[dict], target_email: str, report_date_str: str) -> str:
        md = f"""# 📬 Daily Email Digest - {report_date_str}
**Target Inbox:** `{target_email}`  
**Total Emails:** {len(email_list)}  
*(Fallback report - Gemini API key missing or error occurred)*

---

### 📋 Emails Overview

| # | Date/Time | From | Subject |
|---|-----------|------|---------|
"""
        for idx, item in enumerate(email_list, 1):
            md += f"| {idx} | {item['date']} | {item['sender']} | {item['subject']} |\n"

        md += "\n---\n"
        for idx, item in enumerate(email_list, 1):
            md += f"### Email #{idx}: {item['subject']}\n"
            md += f"**From:** {item['sender']}  \n**Date:** {item['date']}  \n"
            md += f"**Snippet:** {item['body_snippet'][:300]}...\n\n"

        return md
