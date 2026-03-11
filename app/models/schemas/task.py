from datetime import date, datetime

from pydantic import BaseModel

from app.models.db.task import TaskPriority

# ---------------------------------------------------------------------------
# Task Comments
# ---------------------------------------------------------------------------

class TaskCommentCreate(BaseModel):
    author: str
    body: str


class TaskCommentUpdate(BaseModel):
    body: str


class TaskCommentRead(BaseModel):
    id: int
    task_id: int
    author: str
    body: str
    created_at: datetime
    updated_at: datetime | None


# ---------------------------------------------------------------------------
# Task History
# ---------------------------------------------------------------------------

class TaskHistoryRead(BaseModel):
    id: int
    task_id: int
    field_changed: str
    old_value: str | None
    new_value: str | None
    changed_by: str
    changed_at: datetime


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

class TaskCreate(BaseModel):
    project_id: int
    category_id: int
    type_id: int | None = None
    status_id: int | None = None  # If omitted, uses the template's default status
    component_id: int | None = None
    title: str
    description: str | None = None
    assignee: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    start_date: date | None = None
    due_date: date | None = None


class TaskUpdate(BaseModel):
    category_id: int | None = None
    type_id: int | None = None
    status_id: int | None = None
    component_id: int | None = None
    title: str | None = None
    description: str | None = None
    assignee: str | None = None
    priority: TaskPriority | None = None
    start_date: date | None = None
    due_date: date | None = None
    changed_by: str = "system"


class TaskRead(BaseModel):
    id: int
    project_id: int
    category_id: int
    type_id: int | None
    status_id: int
    component_id: int | None
    title: str
    description: str | None
    assignee: str | None
    priority: TaskPriority
    start_date: date | None
    due_date: date | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TaskDetailRead(TaskRead):
    """Task with comments and recent history, used for GET /{task_id}."""
    comments: list[TaskCommentRead] = []
    recent_history: list[TaskHistoryRead] = []


# ---------------------------------------------------------------------------
# Task Summary (aggregate counts for a project)
# ---------------------------------------------------------------------------

class TaskSummary(BaseModel):
    total: int = 0
    by_status: dict[str, int] = {}
    by_category: dict[str, int] = {}
    by_component: dict[str, int] = {}
    by_priority: dict[str, int] = {}