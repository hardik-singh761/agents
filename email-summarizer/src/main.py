import sys
import argparse
# pyrefly: ignore [missing-import]
import schedule
import time
from datetime import datetime, timezone
import logging
from config import GMAIL_EMAIL, GMAIL_APP_PASSWORD, GEMINI_API_KEY, REPORTS_DIR
from email_fetcher import EmailFetcher
from summarizer_agent import EmailSummarizerAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_daily_email_job():
    """
    Main job that fetches emails from the last 24 hours, generates the summary,
    and writes the output to reports/summary_YYYY-MM-DD.md.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    logging.info(f"=== Starting Daily Email Summary Job for {today_str} ===")

    if not GMAIL_APP_PASSWORD:
        logging.error("GMAIL_APP_PASSWORD is missing in .env! Please set your 16-character App Password.")
        print("\n❌ ERROR: GMAIL_APP_PASSWORD missing in .env file.")
        print("Follow instructions in README.md to generate an App Password from https://myaccount.google.com/apppasswords\n")
        return

    try:
        fetcher = EmailFetcher(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
        emails = fetcher.fetch_emails_last_24h(hours=24)

        agent = EmailSummarizerAgent(GEMINI_API_KEY)
        summary_md = agent.generate_summary(emails, GMAIL_EMAIL, today_str)

        output_filename = REPORTS_DIR / f"summary_{today_str}.md"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(summary_md)

        logging.info(f"Daily summary successfully saved to: {output_filename}")
        try:
            print(f"\n[+] Daily Summary Report Generated Successfully!")
            print(f"[+] Report File: {output_filename}\n")
        except UnicodeEncodeError:
            pass

    except Exception as e:
        logging.error(f"Error during daily email job execution: {e}", exc_info=True)

def main():
    parser = argparse.ArgumentParser(description="Atomic Email Summarizer Agent for officialhardik2003@gmail.com")
    parser.add_argument("--now", action="store_true", help="Run email summarization job immediately")
    parser.add_argument("--schedule", action="store_true", help="Run in daemon mode scheduled daily at 08:00 AM")
    args = parser.parse_args()

    if args.schedule:
        logging.info("Starting Email Summarizer Agent in daemon mode scheduled daily at 08:00 AM...")
        schedule.every().day.at("08:00").do(run_daily_email_job)
        print("⏰ Agent is running and waiting for 08:00 AM daily trigger. Press Ctrl+C to exit.")
        while True:
            schedule.run_pending()
            time.sleep(30)
    else:
        # Default behavior or --now
        run_daily_email_job()

if __name__ == "__main__":
    main()
