from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from src.db import async_session
from src.models import Task
import asyncio

scheduler = AsyncIOScheduler()

async def _scan_overdue_and_due_soon():
    async with async_session() as session:
        now = datetime.now(timezone.utc)
        soon = now + timedelta(hours=24)
        result = await session.execute(select(Task))
        tasks = result.scalars().all()
        due_soon, overdue = [], []
        for t in tasks:
            if t.due_at:
                if t.due_at < now and t.status != "done":
                    t.is_overdue = True
                    overdue.append(t)
                elif now <= t.due_at <= soon and t.status != "done":
                    due_soon.append(t)
        await session.commit()
        # TODO: send Slack / email notifications here
        if overdue or due_soon:
            print(f"[reminders] overdue={len(overdue)} due_soon={len(due_soon)}")  # placeholder

def start_scheduler():
    scheduler.add_job(_scan_overdue_and_due_soon, CronTrigger(minute="*/15"))
    scheduler.start()
