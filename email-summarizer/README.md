# 📬 Daily Email Summarizer Agent

An AI agent that connects to your Gmail inbox, retrieves all emails received over the past 24 hours (from 8:00 AM previous day to 8:00 AM current day), generates an executive daily digest using Google Gemini AI, and outputs a clean Markdown report.

---

## 📋 What You Need To Do (2 Quick Steps)

### Step 1: Generate a Gmail App Password
Because Google disables plain password access for security:
1. Go to your Google Account Security settings: **[https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)**
   *(Ensure 2-Step Verification is enabled on `officialhardik2003@gmail.com`)*
2. Under "App name", type `Email Summarizer Agent` and click **Create**.
3. Copy the 16-character generated passcode (e.g., `abcd efgh ijkl mnop`).

### Step 2: Get a Gemini API Key (Free)
1. Visit Google AI Studio: **[https://aistudio.google.com/app/api-keys](https://aistudio.google.com/app/api-keys)**
2. Click **Create API key** and copy it.

---

## ⚙️ Configuration

Open the `.env` file in this directory and paste your details:

```env
GMAIL_EMAIL=officialhardik2003@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password_here
GEMINI_API_KEY=your_gemini_api_key_here
REPORTS_DIR=reports
```

---

## 🚀 Running & Testing The Agent

### Test Run Immediately (Now)
From the `email-summarizer/` directory, run:
```bash
.\venv\Scripts\python src\main.py --now
```
This will fetch emails from the last 24 hours right away and save your daily report to:
`email-summarizer\reports\summary_YYYY-MM-DD.md`

---

## ⏰ Scheduling 8:00 AM Daily Run

### Method A: Windows Task Scheduler (Recommended - Runs automatically in the background)
From the `email-summarizer/` directory, run this command once in PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File .\setup_task_scheduler.ps1
```
This registers a task in Windows that will trigger `src\main.py` every morning at **08:00 AM** automatically!

### Method B: Daemon Mode
Keep the script running continuously in a terminal window:
```bash
.\venv\Scripts\python src\main.py --schedule
```

---

## 🛠️ Setup (First Time)

Create a virtual environment and install dependencies:
```bash
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
```

---

## 📁 Output Structure

Daily summaries will be stored in `reports/`:
- `reports/summary_2026-08-09.md`
- `reports/summary_2026-08-10.md`
- ...

Each `.md` file contains:
- 🚨 **Action Items & Priority Emails**
- 📊 **Executive Key Updates**
- 📋 **Structured Table of All Received Emails**
