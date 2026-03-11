from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id", index=True)
    category_id: int = Field(foreign_key="task_categories.id", index=True)
    type_id: int | None = Field(default=None, foreign_key="task_types.id")
    status_id: int = Field(foreign_key="status_definitions.id", index=True)
    component_id: int | None = Field(default=None, foreign_key="project_components.id")
    title: str = Field(max_length=300)
    description: str | None = Field(default=None)
    assignee: str | None = Field(default=None, max_length=200)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    start_date: date | None = Field(default=None)
    due_date: date | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    project: "Project" = Relationship(back_populates="tasks")
    comments: list["TaskComment"] = Relationship(back_populates="task")
    history: list["TaskHistory"] = Relationship(back_populates="task")


class TaskComment(SQLModel, table=True):
    __tablename__ = "task_comments"

    id: int | None = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    author: str = Field(max_length=200)
    body: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default=None)

    # Relationships
    task: Task = Relationship(back_populates="comments")


class TaskHistory(SQLModel, table=True):
    __tablename__ = "task_history"

    id: int | None = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    field_changed: str = Field(max_length=100)
    old_value: str | None = Field(default=None)
    new_value: str | None = Field(default=None)
    changed_by: str = Field(max_length=200)
    changed_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: Task = Relationship(back_populates="history")




if TYPE_CHECKING:
    from app.models.db.project import Project