from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "pm-bot")
    env: str = os.getenv("ENV", "dev")
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./pm_bot.db")
    tz: str = os.getenv("TZ", "America/Chicago")
    slack_bot_token: str | None = os.getenv("SLACK_BOT_TOKEN")
    slack_signing_secret: str | None = os.getenv("SLACK_SIGNING_SECRET")
    jira_base_url: str | None = os.getenv("JIRA_BASE_URL")
    jira_email: str | None = os.getenv("JIRA_EMAIL")
    jira_api_token: str | None = os.getenv("JIRA_API_TOKEN")
    github_token: str | None = os.getenv("GITHUB_TOKEN")

settings = Settings()
