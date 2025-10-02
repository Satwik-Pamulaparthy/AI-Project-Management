from slack_bolt.adapter.starlette.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp
from starlette.requests import Request
from src.config import settings
from src.nlu import route_intent
from src.services import tasks as task_service
from src.schemas import TaskCreate, TaskUpdate
from datetime import datetime

slack_app = AsyncApp(token=settings.slack_bot_token, signing_secret=settings.slack_signing_secret)
app_handler = AsyncSlackRequestHandler(slack_app)

@slack_app.event("app_mention")
async def handle_app_mention(body, say, logger):
    text = body.get("event", {}).get("text", "")
    reply = await route_intent(text)
    await say(reply)

@slack_app.message("status")
async def handle_status(message, say):
    await say("Try: 'status project <id>' or 'status task <id>'" )

async def slack_events(request: Request):
    return await app_handler.handle(request)
