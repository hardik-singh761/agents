# 🤖 Agents Hub

A personal AI agent framework. Each agent runs **autonomously in the cloud** via GitHub Actions — no laptop needed. Add a new agent by dropping a folder + workflow file.

---

## 🔥 How It Works

```
GitHub Actions (free cloud servers)
    ├── ⏰ 7:00 AM IST → daily-news-briefing runs → delivers AI news digest
    ├── ⏰ 7:00 AM IST → freelance-gig-finder runs → delivers gig digest
    ├── ⏰ 8:00 AM IST → email-summarizer runs → emails you the digest
    └── ⏰ ???         → your-next-agent runs → delivers results
```

Each agent:
1. Wakes up on its own schedule (cron)
2. Runs on GitHub's free Ubuntu cloud machine
3. Does its job (fetch data, call APIs, generate reports)
4. Delivers results (email, Slack, webhook, etc.)
5. Machine shuts down. Cost: **$0**.

---

## 📂 Available Agents

| Agent | Description | Schedule | Delivery |
|-------|-------------|----------|----------|
| [daily-news-briefing](./daily-news-briefing/) | Curates & summarizes AI/tech news from HackerNews, ProductHunt, etc. | 7:00 AM IST | 📧 Email |
| [freelance-gig-finder](./freelance-gig-finder/) | Scrapes Upwork, RemoteOK, and Freelancer, ranks gigs using Gemini | 7:00 AM IST | 📧 Email |
| [email-summarizer](./email-summarizer/) | Daily Gmail inbox digest powered by Gemini AI | 8:00 AM IST | 📧 Email |

---

## 🏗️ Project Structure

```
agents/
├── .github/workflows/          ← GitHub Actions (cloud schedules)
│   ├── daily-news-briefing.yml ← runs news agent daily at 7 AM
│   ├── freelance-gig-finder.yml← runs gig finder daily at 7 AM
│   ├── email-summarizer.yml    ← runs email agent daily at 8 AM
│   └── README.md               ← workflow template for new agents
├── README.md                   ← You are here
├── .gitignore
│
├── shared/                     ← Shared utility code (e.g. mailer)
│
├── email-summarizer/           ← Agent 1
│   ├── README.md
│   ├── .env / .env.example
│   ├── requirements.txt
│   └── src/
│       ├── main.py
│       ├── config.py
│       ├── email_fetcher.py
│       ├── summarizer_agent.py
│       └── report_mailer.py
│
└── <your-next-agent>/          ← Agent 2, 3, ... (just add a folder!)
```

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
2. **Add source code**: `src/main.py`, `requirements.txt`, `.env.example`, `README.md`
3. **Create a workflow**: Copy the template from [`.github/workflows/README.md`](./.github/workflows/README.md)
4. **Add secrets**: Any new API keys go to GitHub Secrets
5. **Push**. It runs autonomously from now on.

---

## 🛠️ Running Agents Locally

Each agent can also run on your local machine:

```bash
cd email-summarizer
.\venv\Scripts\python src\main.py --now           # run + save report
.\venv\Scripts\python src\main.py --now --email    # run + save + email report
```
