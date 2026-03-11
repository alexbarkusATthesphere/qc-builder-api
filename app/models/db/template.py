from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

from app.models.db.project import Project


class Template(SQLModel, table=True):
    __tablename__ = "templates"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=200, index=True)
    description: str | None = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    statuses: list["StatusDefinition"] = Relationship(back_populates="template")
    categories: list["TaskCategory"] = Relationship(back_populates="template")
    projects: list["Project"] = Relationship(back_populates="template")


class StatusDefinition(SQLModel, table=True):
    __tablename__ = "status_definitions"

    id: int | None = Field(default=None, primary_key=True)
    template_id: int = Field(foreign_key="templates.id", index=True)
    name: str = Field(max_length=100)
    color: str | None = Field(default=None, max_length=7)
    display_order: int = Field(default=0)
    is_default: bool = Field(default=False)
    is_terminal: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    template: Template = Relationship(back_populates="statuses")


class TaskCategory(SQLModel, table=True):
    __tablename__ = "task_categories"

    id: int | None = Field(default=None, primary_key=True)
    template_id: int = Field(foreign_key="templates.id", index=True)
    name: str = Field(max_length=150)
    description: str | None = Field(default=None)
    display_order: int = Field(default=0)
    icon: str | None = Field(default=None, max_length=50)
    color: str | None = Field(default=None, max_length=7)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    template: Template = Relationship(back_populates="categories")
    types: list["TaskType"] = Relationship(back_populates="category")


class TaskType(SQLModel, table=True):
    __tablename__ = "task_types"

    id: int | None = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="task_categories.id", index=True)
    name: str = Field(max_length=150)
    description: str | None = Field(default=None)
    display_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    category: TaskCategory = Relationship(back_populates="types")