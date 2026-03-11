from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel


class ProjectStatus(StrEnum):
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETE = "complete"
    ARCHIVED = "archived"


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: int | None = Field(default=None, primary_key=True)
    template_id: int = Field(foreign_key="templates.id", index=True)
    name: str = Field(max_length=250, index=True)
    description: str | None = Field(default=None)
    owner: str | None = Field(default=None, max_length=200)
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE)
    start_date: date | None = Field(default=None)
    target_end_date: date | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    template: "Template" = Relationship(back_populates="projects")
    components: list["ProjectComponent"] = Relationship(back_populates="project")
    tasks: list["Task"] = Relationship(back_populates="project")


class ProjectComponent(SQLModel, table=True):
    __tablename__ = "project_components"

    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id", index=True)
    name: str = Field(max_length=150)
    description: str | None = Field(default=None)
    display_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    project: Project = Relationship(back_populates="components")


# Forward references resolved in models/db/__init__.py
if TYPE_CHECKING:
    from app.models.db.task import Task
    from app.models.db.template import Template