from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload
from src.db import async_session
from src.models import Task, Project
from datetime import datetime, timezone

async def create_task(data):
    async with async_session() as session:
        # validate project exists
        proj = await session.get(Project, data.project_id)
        if not proj:
            raise ValueError("Project not found")
        task = Task(
            project_id=data.project_id,
            title=data.title,
            description=data.description,
            assignee_id=data.assignee_id,
            due_at=data.due_at,
            priority=data.priority,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task

async def list_tasks(project_id: int | None = None, status: str | None = None):
    async with async_session() as session:
        stmt = select(Task).options(selectinload(Task.assignee)).order_by(Task.priority, Task.due_at)
        if project_id:
            stmt = stmt.where(Task.project_id == project_id)
        if status:
            stmt = stmt.where(Task.status == status)
        res = await session.execute(stmt)
        return res.scalars().all()

async def update_task(task_id: int, data):
    async with async_session() as session:
        task = await session.get(Task, task_id)
        if not task:
            raise ValueError("Task not found")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        if task.due_at and isinstance(task.due_at, datetime):
            if task.due_at.tzinfo is None:
                task.due_at = task.due_at.replace(tzinfo=timezone.utc)
        await session.commit()
        await session.refresh(task)
        return task
