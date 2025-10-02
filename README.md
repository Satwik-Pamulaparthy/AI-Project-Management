# Project Management & Workflow Automation Bot — Starter Kit (Python)

This repo is a **minimal, modular** scaffold to build a conversational PM bot that can:
- Automate task assignments & deadline reminders
- Provide real-time project progress updates
- Facilitate communication through a chat interface (Slack-ready stubs)
- (Optional) Learn to anticipate workflow bottlenecks with simple heuristics/ML later

## Quick Start (local)

1) **Install** (Python 3.10+ recommended):
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```
2) **Run DB** (uses SQLite by default; Postgres optional via env vars in `.env`):
```bash
uvicorn src.app:app --reload
```
3) Open: `http://127.0.0.1:8000/docs` (interactive API docs).

### Enabling Slack (optional)
- Create a Slack app → add **Bots** & **Events** (message.channels, message.im) and **Slash Commands** (e.g. `/pm`).
- Set `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET` in `.env`.
- Expose your FastAPI locally via a tunnel (e.g., `ngrok http 8000`) and set your Slack Request URL to `https://<your-forwarding-url>/slack/events`.
- Start the app again.

### Enabling Jira / GitHub (optional)
- Add credentials to `.env` (see examples) and fill the stubs in `src/integrations/` if you want real data.

---

## Architecture

- **FastAPI** http app (`src/app.py`) + **APScheduler** for reminders (`src/scheduler.py`).
- **SQLAlchemy** models (`src/models.py`) with a thin service layer in `src/services/`.
- **NLU**: a compact rule/regex intent router (`src/nlu.py`) that you can later upgrade to an LLM or Rasa/Haystack.
- **Integrations**: stubs for Slack, Jira, GitHub in `src/integrations/`.
- **Progress & bottlenecks**: heuristics in `src/services/progress.py` you can improve iteratively.

---

## Suggested Roadmap

1. **MVP (Day 1–3)**: Local API + SQLite + basic CRUD for projects/tasks + reminders.
2. **Chat Loop (Day 4–5)**: Slack events endpoint + rule-based intents (`assign`, `remind`, `status`, `help`).
3. **Integrations (Week 2)**: Read-only Jira & GitHub to compute progress; post daily digest to Slack.
4. **Learning (Week 3–4)**: Collect features (lead time, WIP, PR age) → train a simple model to flag bottlenecks.
5. **Hardening (Ongoing)**: Auth, RBAC, migrations, better testing, observability.

---

## Example Intents

- **Assign**: "assign @alice to ‘Write API spec’ due tomorrow"
- **Remind**: "remind me if any task is due in 24h"
- **Status**: "what's the progress on Backend Revamp?"
- **Blockers**: "show likely bottlenecks this week"

---

## Testing

```bash
pytest -q
```

---

## Notes

- Keep secrets in `.env`. Never commit them.
- Start with the rule-based `nlu.py`. Swap it out for an LLM tool-calling layer when you're ready.
- The code defaults to **SQLite** to simplify local dev. Switch to Postgres by setting `DATABASE_URL`.
