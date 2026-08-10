import sys
import os
import argparse
import logging
from datetime import datetime

# Add parent's parent to path so shared modules can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from config import GMAIL_EMAIL, GMAIL_APP_PASSWORD, GEMINI_API_KEY, REPORTS_DIR
from news_fetcher import NewsFetcher
from news_summarizer import NewsSummarizer

# Import the mailer from email-summarizer (reuse, don't duplicate)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "email-summarizer", "src"))
from report_mailer import ReportMailer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_news_briefing(send_email: bool = False):
    """Main job: fetch news, summarize with Gemini, save report, optionally email."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    logging.info(f"=== Starting Daily News Briefing for {today_str} ===")

    if not GEMINI_API_KEY:
        logging.error("GEMINI_API_KEY is missing!")
        print("\n[!] ERROR: GEMINI_API_KEY missing in .env or GitHub Secrets.\n")
        return

    try:
        # 1. Fetch news from all sources
        fetcher = NewsFetcher()
        stories = fetcher.fetch_all(hours=24)

        # 2. Generate briefing with Gemini
        summarizer = NewsSummarizer(GEMINI_API_KEY)
        briefing_md = summarizer.generate_briefing(stories, today_str)

        # 3. Save to reports/
        output_file = REPORTS_DIR / f"briefing_{today_str}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(briefing_md)

        logging.info(f"Briefing saved to: {output_file}")
        try:
            print(f"\n[+] Daily News Briefing Generated!")
            print(f"[+] Report: {output_file}\n")
        except UnicodeEncodeError:
            pass

        # 4. Email if requested
        if send_email and GMAIL_APP_PASSWORD:
            mailer = ReportMailer(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
            subject = f"\U0001f4f0 Daily Tech Briefing \u2014 {today_str}"
            success = mailer.send_report(subject, briefing_md, GMAIL_EMAIL)
            if success:
                logging.info(f"Briefing emailed to {GMAIL_EMAIL}")
            else:
                logging.error(f"Failed to email briefing")

    except Exception as e:
        logging.error(f"Error during news briefing: {e}", exc_info=True)


def main():
    parser = argparse.ArgumentParser(description="Daily News Briefing Agent")
    parser.add_argument("--email", action="store_true", help="Email the briefing to your inbox")
    args = parser.parse_args()
    run_news_briefing(send_email=args.email)


if __name__ == "__main__":
    main()
