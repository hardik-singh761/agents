# 🤖 Agent Workflows Guide

Each agent in this repo gets its own GitHub Actions workflow file for autonomous cloud execution.

## How It Works

- Each `.yml` file here corresponds to one agent
- Agents run on GitHub's free Ubuntu cloud machines
- Secrets (API keys, passwords) are stored in GitHub Secrets (Settings → Secrets → Actions)
- Each workflow is independent — adding/removing an agent doesn't affect others

## Creating a Workflow for a New Agent

Copy this template and save as `<agent-name>.yml`:

```yaml
name: "🤖 <Agent Display Name>"

on:
  schedule:
    # Set your cron schedule (UTC timezone)
    # Use https://crontab.guru to build your expression
    # Example: 8:00 AM IST = 2:30 AM UTC → "30 2 * * *"
    - cron: "YOUR_CRON_HERE"

  # Always include this for manual testing
  workflow_dispatch:

jobs:
  run-agent:
    name: "🚀 Run <Agent Name>"
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: <agent-folder-name>

    steps:
      - name: "📥 Checkout repository"
        uses: actions/checkout@v4

      - name: "🐍 Setup Python"
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: "📦 Install dependencies"
        run: pip install -r requirements.txt

      - name: "🚀 Run Agent"
        env:
          # Add your agent's secrets here
          # Each secret must be added in GitHub repo Settings → Secrets → Actions
          MY_SECRET: ${{ secrets.MY_SECRET }}
        run: python src/main.py
```

## Common Cron Schedules (UTC)

| IST Time | UTC Cron | Expression |
|----------|----------|------------|
| 6:00 AM  | 12:30 AM | `30 0 * * *` |
| 8:00 AM  | 2:30 AM  | `30 2 * * *` |
| 9:00 AM  | 3:30 AM  | `30 3 * * *` |
| 12:00 PM | 6:30 AM  | `30 6 * * *` |
| 6:00 PM  | 12:30 PM | `30 12 * * *` |
| Every 6h | —        | `0 */6 * * *` |
| Mon-Fri  | 2:30 AM  | `30 2 * * 1-5` |

## Active Workflows

| Workflow | Agent | Schedule |
|----------|-------|----------|
| `email-summarizer.yml` | Email Summarizer | Daily 8:00 AM IST |
