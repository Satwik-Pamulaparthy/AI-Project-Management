from pydantic import BaseModel, Field
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    external_ref: str | None = None

class UserOut(BaseModel):
    id: int
    name: str
    external_ref: str | None
    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    name: str
    description: str | None = None

class ProjectOut(BaseModel):
    id: int
    name: str
    description: str | None
    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    project_id: int
    title: str
    description: str | None = None
    assignee_id: int | None = None
    due_at: datetime | None = None
    priority: int = Field(ge=1, le=5, default=3)

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: int | None = None
    due_at: datetime | None = None
    status: str | None = None
    priority: int | None = None

class TaskOut(BaseModel):
    id: int
    project_id: int
    title: str
    description: str | None
    assignee_id: int | None
    due_at: datetime | None
    status: str
    priority: int
    is_overdue: bool
    class Config:
        from_attributes = True
