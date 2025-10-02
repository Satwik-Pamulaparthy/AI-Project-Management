from fastapi import FastAPI, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import AsyncGenerator
from sqlalchemy import text
from src.db import engine, async_session, Base
from src.models import *
from src.schemas import *
from src.services import tasks as task_service
from src.scheduler import start_scheduler
from src.integrations.slack import slack_events

app = FastAPI(title="PM Bot API", version="0.1.0")

# add this import near the top
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PM Bot API", version="0.1.0")

# add this block immediately after the app = FastAPI(...) line
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, PATCH, DELETE, etc.
    allow_headers=["*"],   # Authorization, Content-Type, etc.
)


@app.get("/")
async def home():
    return {
        "app": "PM Bot API",
        "docs": "/docs",
        "health": "/health",
        "tip": "Use POST /tasks to create tasks; GET /tasks to list."
    }

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    start_scheduler()

@app.get("/health")
async def health():
    return {"ok": True}

# --- CRUD: projects/users minimal demo (tasks full) ---
@app.post("/tasks", response_model=TaskOut)
async def create_task(data: TaskCreate):
    task = await task_service.create_task(data)
    return task

@app.get("/tasks", response_model=list[TaskOut])
async def list_tasks(project_id: int | None = None, status: str | None = None):
    return await task_service.list_tasks(project_id, status)

@app.patch("/tasks/{task_id}", response_model=TaskOut)
async def update_task(task_id: int, data: TaskUpdate):
    return await task_service.update_task(task_id, data)

# --- Slack Events endpoint ---
@app.post("/slack/events")
async def slack_events_endpoint(request: Request):
    return await slack_events(request)

from src.schemas import UserCreate, UserOut, ProjectCreate, ProjectOut
from src.models import User, Project
from sqlalchemy import select

@app.post("/projects", response_model=ProjectOut)
async def create_project(data: ProjectCreate):
    async with async_session() as s:
        p = Project(name=data.name, description=data.description)
        s.add(p)
        await s.commit()
        await s.refresh(p)
        return p

@app.get("/projects", response_model=list[ProjectOut])
async def list_projects():
    async with async_session() as s:
        rows = await s.execute(select(Project))
        return rows.scalars().all()

@app.post("/users", response_model=UserOut)
async def create_user(data: UserCreate):
    async with async_session() as s:
        u = User(name=data.name, external_ref=data.external_ref)
        s.add(u)
        await s.commit()
        await s.refresh(u)
        return u

@app.get("/users", response_model=list[UserOut])
async def list_users():
    async with async_session() as s:
        rows = await s.execute(select(User))
        return rows.scalars().all()
