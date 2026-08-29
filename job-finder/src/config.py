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

# ─── Target Roles ───────────────────────────────────────────────
TARGET_ROLES = [
    "AI Engineer",
    "GenAI Engineer",
    "Generative AI Engineer",
    "Agentic AI Engineer",
    "Machine Learning Engineer",
    "Data Scientist",
    "ML Engineer",
    "AI Developer",
    "LLM Engineer",
    "NLP Engineer",
    "Applied AI Engineer",
    "Deep Learning Engineer",
]

# Keywords to match in job titles / descriptions
SEARCH_KEYWORDS = [
    "ai engineer",
    "gen ai",
    "genai",
    "generative ai",
    "agentic ai",
    "data scientist",
    "machine learning",
    "ml engineer",
    "deep learning",
    "nlp engineer",
    "llm",
    "large language model",
    "ai developer",
    "applied ai",
    "computer vision",
    "data science",
]

# Experience level keywords to prefer (fresher / entry-level)
EXPERIENCE_KEYWORDS = [
    "fresher",
    "entry level",
    "entry-level",
    "junior",
    "0-1 year",
    "0-2 year",
    "0-3 year",
    "1-2 year",
    "1-3 year",
    "new grad",
    "graduate",
    "associate",
    "intern",
    "trainee",
]

# Target companies (big/good companies to prioritize)
TARGET_COMPANIES = [
    "google", "microsoft", "amazon", "meta", "apple", "nvidia",
    "openai", "anthropic", "deepmind", "cohere", "stability ai",
    "dell", "ibm", "oracle", "salesforce", "adobe", "intel",
    "samsung", "qualcomm", "cisco", "vmware", "sap",
    "tcs", "infosys", "wipro", "hcl", "tech mahindra",
    "flipkart", "swiggy", "zomato", "razorpay", "cred",
    "meesho", "paytm", "phonepe", "ola", "byju",
    "jio", "reliance", "accenture", "deloitte", "ey", "kpmg", "pwc",
    "morgan stanley", "goldman sachs", "jpmorgan", "deutsche bank",
    "walmart", "uber", "airbnb", "stripe", "databricks",
    "snowflake", "palantir", "datadog", "confluent",
    "atlassian", "servicenow", "workday", "zoom",
    "hugging face", "langchain", "together ai",
]

# Locations to search
LOCATIONS = ["India", "Remote", "Bangalore", "Hyderabad", "Pune", "Delhi", "Mumbai", "Gurgaon", "Noida"]
