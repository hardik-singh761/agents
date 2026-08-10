import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

GMAIL_EMAIL = os.getenv("GMAIL_EMAIL", "officialhardik2003@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
REPORTS_DIR = BASE_DIR / os.getenv("REPORTS_DIR", "reports")

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
