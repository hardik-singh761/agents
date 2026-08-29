# 🤖 Agents Hub

A personal AI agent framework. Each agent runs **autonomously in the cloud** via GitHub Actions — no laptop needed. Add a new agent by dropping a folder + workflow file.

---

## 🔥 How It Works

```
GitHub Actions (free cloud servers)
    ├── ⏰ 7:00 AM IST → job-finder runs        → delivers job digest
    ├── ⏰ 8:00 AM IST → email-summarizer runs   → emails inbox digest
    ├── 💤 DISABLED    → daily-news-briefing      → (can re-enable anytime)
    └── 💤 DISABLED    → freelance-gig-finder     → (can re-enable anytime)
```

Each agent:
1. Wakes up on its own schedule (cron)
2. Runs on GitHub's free Ubuntu cloud machine
3. Does its job (fetch data, call APIs, generate reports)
4. Delivers results (email, Slack, webhook, etc.)
5. Machine shuts down. Cost: **$0**.

---

## 📂 Available Agents

| Agent | Description | Schedule | Status |
|-------|-------------|----------|--------|
| [job-finder](./job-finder/) | Finds AI/ML/Data Science/GenAI jobs at top companies, ranks by relevance for freshers | 7:00 AM IST | ✅ Active |
| [email-summarizer](./email-summarizer/) | Daily Gmail inbox digest powered by Gemini AI | 8:00 AM IST | ✅ Active |
| [daily-news-briefing](./daily-news-briefing/) | Curates & summarizes AI/tech news from HackerNews, ProductHunt, etc. | Manual only | 💤 Disabled |
| [freelance-gig-finder](./freelance-gig-finder/) | Scrapes Upwork, RemoteOK, and Freelancer, ranks gigs using Gemini | Manual only | 💤 Disabled |

---

## 🏗️ Project Structure

```
agents/
├── .github/workflows/          ← GitHub Actions (cloud schedules)
│   ├── job-finder.yml          ← runs job finder daily at 7 AM ✅
│   ├── email-summarizer.yml    ← runs email agent daily at 8 AM ✅
│   ├── daily-news-briefing.yml ← DISABLED (manual trigger only)
│   ├── freelance-gig-finder.yml← DISABLED (manual trigger only)
│   └── README.md               ← workflow template for new agents
├── README.md                   ← You are here
├── .gitignore
│
├── shared/                     ← Shared utility code (e.g. mailer)
│
├── job-finder/                 ← AI/ML/DS Job Finder Agent
│   ├── .env.example
│   ├── requirements.txt
│   └── src/
│       ├── main.py             ← Entry point
│       ├── config.py           ← Target roles, companies, keywords
│       ├── job_fetcher.py      ← Scrapes 7 job sources
│       └── job_analyzer.py     ← Gemini-powered ranking & digest
│
├── email-summarizer/           ← Gmail Inbox Summarizer Agent
│   ├── README.md
│   ├── .env.example
│   ├── requirements.txt
│   └── src/
│       ├── main.py
│       ├── config.py
│       ├── email_fetcher.py
│       ├── summarizer_agent.py
│       └── report_mailer.py    ← Shared mailer (used by all agents)
│
├── daily-news-briefing/        ← News Briefing Agent (disabled)
│
└── freelance-gig-finder/       ← Freelance Gig Finder (disabled)
```

---

## 🎯 Job Finder Agent — Sources

The job-finder agent scrapes **7 free sources** daily (no API keys needed beyond Gemini):

| Source | Type | What It Finds |
|--------|------|---------------|
| RemoteOK | JSON API | Remote AI/ML jobs worldwide |
| Himalayas | RSS Feed | Curated remote tech roles |
| Remotive | RSS Feed | Remote-first company jobs |
| Arbeitnow | JSON API | Global + India job listings |
| HN Who's Hiring | API | Startup & big-tech roles (monthly threads) |
| WorkAnywhere | RSS Feed | Developer/AI-focused remote jobs |
| LinkedIn (via Google) | Web Search | Public LinkedIn job posts |

Jobs are filtered for: `AI Engineer`, `GenAI Engineer`, `Data Scientist`, `ML Engineer`, `Agentic AI`, `LLM Engineer`, `NLP Engineer`, `Deep Learning`, and ranked by relevance to a **fresher/entry-level** profile.

---

## 🔐 GitHub Secrets Setup (One-Time)

Go to **[repo Settings → Secrets → Actions](https://github.com/hardik-singh761/agents/settings/secrets/actions)** and add:

| Secret Name | Description |
|-------------|-------------|
| `GMAIL_EMAIL` | `officialhardik2003@gmail.com` |
| `GMAIL_APP_PASSWORD` | 16-char Gmail App Password |
| `GEMINI_API_KEY` | Google Gemini API key |

> Secrets are encrypted and never exposed in logs. Each agent can share or have its own secrets.

---

## ➕ Adding a New Agent

1. **Create the agent folder**: `agents/<agent-name>/`
2. **Add source code**: `src/main.py`, `requirements.txt`, `.env.example`
3. **Create a workflow**: `.github/workflows/<agent-name>.yml`
4. **Add secrets**: Any new API keys go to GitHub Secrets
5. **Push**. It runs autonomously from now on.

---

## 🛠️ Running Agents Locally

Each agent can also run on your local machine:

```bash
# Job Finder
cd job-finder
.\venv\Scripts\python src\main.py             # run + save report
.\venv\Scripts\python src\main.py --email      # run + save + email report

# Email Summarizer
cd email-summarizer
.\venv\Scripts\python src\main.py --now        # run + save report
.\venv\Scripts\python src\main.py --now --email # run + save + email report
```
