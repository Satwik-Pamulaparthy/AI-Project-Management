from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, func, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_ref: Mapped[str | None] = mapped_column(String(128), index=True)  # slack id / email
    name: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="project")

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(250))
    description: Mapped[str | None] = mapped_column(Text())
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(50), default="todo")  # todo/in_progress/done/blocked
    priority: Mapped[int] = mapped_column(Integer, default=3)  # 1 high - 5 low
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    is_overdue: Mapped[bool] = mapped_column(Boolean, default=False)

    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    assignee: Mapped["User"] = relationship("User")

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(String(100))  # created_task, status_change, comment, reminder_sent
    payload: Mapped[str | None] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
