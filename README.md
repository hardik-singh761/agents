# 🤖 Agents Hub

A collection of personal AI automation agents. Each agent lives in its own self-contained directory with its own config, dependencies, and virtual environment.

---

## 📂 Available Agents

| Agent | Description | Status |
|-------|-------------|--------|
| [email-summarizer](./email-summarizer/) | Daily Gmail inbox digest powered by Gemini AI | ✅ Active |

---

## 🏗️ Structure

```
agents/
├── README.md              ← You are here
├── .gitignore
├── email-summarizer/      ← Each agent is a self-contained directory
│   ├── README.md          ← Agent-specific docs & setup
│   ├── .env               ← Agent-specific secrets
│   ├── requirements.txt   ← Agent-specific dependencies
│   ├── src/               ← Source code
│   ├── reports/           ← Output files
│   └── venv/              ← Agent-specific virtual environment
└── <your-next-agent>/     ← Add new agents here!
```

## ➕ Adding a New Agent

1. Create a new directory: `agents/<agent-name>/`
2. Add a `README.md` with setup instructions
3. Add `requirements.txt`, `.env.example`, and `src/` folder
4. Each agent manages its own `venv/` and `.env`

That's it — no changes needed to existing agents!
