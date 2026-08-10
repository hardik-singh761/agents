import sys
import os
import argparse
import logging
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from config import GMAIL_EMAIL, GMAIL_APP_PASSWORD, GEMINI_API_KEY, REPORTS_DIR, SEARCH_KEYWORDS
from gig_fetcher import GigFetcher
from gig_analyzer import GigAnalyzer

# Reuse mailer from email-summarizer
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "email-summarizer", "src"))
from report_mailer import ReportMailer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_gig_finder(send_email: bool = False):
    """Main job: fetch gigs, analyze with Gemini, save report, optionally email."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    logging.info(f"=== Starting Freelance Gig Finder for {today_str} ===")

    if not GEMINI_API_KEY:
        logging.error("GEMINI_API_KEY is missing!")
        print("\n[!] ERROR: GEMINI_API_KEY missing in .env or GitHub Secrets.\n")
        return

    try:
        # 1. Fetch gigs from all sources
        fetcher = GigFetcher(SEARCH_KEYWORDS)
        gigs = fetcher.fetch_all()

        # 2. Analyze and rank with Gemini
        analyzer = GigAnalyzer(GEMINI_API_KEY)
        digest_md = analyzer.generate_digest(gigs, today_str)

        # 3. Save to reports/
        output_file = REPORTS_DIR / f"gigs_{today_str}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(digest_md)

        logging.info(f"Gig digest saved to: {output_file}")
        try:
            print(f"\n[+] Freelance Gig Digest Generated!")
            print(f"[+] Report: {output_file}\n")
        except UnicodeEncodeError:
            pass

        # 4. Email if requested
        if send_email and GMAIL_APP_PASSWORD:
            mailer = ReportMailer(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
            subject = f"\U0001f4bc Freelance Gig Digest \u2014 {today_str}"
            success = mailer.send_report(subject, digest_md, GMAIL_EMAIL)
            if success:
                logging.info(f"Gig digest emailed to {GMAIL_EMAIL}")
            else:
                logging.error(f"Failed to email gig digest")

    except Exception as e:
        logging.error(f"Error during gig finder: {e}", exc_info=True)


def main():
    parser = argparse.ArgumentParser(description="Freelance Gig Finder Agent")
    parser.add_argument("--email", action="store_true", help="Email the digest to your inbox")
    args = parser.parse_args()
    run_gig_finder(send_email=args.email)


if __name__ == "__main__":
    main()
