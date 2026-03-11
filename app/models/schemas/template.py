from datetime import datetime

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Status Definitions
# ---------------------------------------------------------------------------

class StatusDefinitionCreate(BaseModel):
    name: str
    color: str | None = None
    display_order: int = 0
    is_default: bool = False
    is_terminal: bool = False


class StatusDefinitionUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    display_order: int | None = None
    is_default: bool | None = None
    is_terminal: bool | None = None


class StatusDefinitionRead(BaseModel):
    id: int
    template_id: int
    name: str
    color: str | None
    display_order: int
    is_default: bool
    is_terminal: bool
    created_at: datetime


class StatusReorderItem(BaseModel):
    id: int
    display_order: int


class StatusReorderRequest(BaseModel):
    statuses: list[StatusReorderItem]


# ---------------------------------------------------------------------------
# Task Types
# ---------------------------------------------------------------------------

class TaskTypeCreate(BaseModel):
    name: str
    description: str | None = None
    display_order: int = 0


class TaskTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    display_order: int | None = None


class TaskTypeRead(BaseModel):
    id: int
    category_id: int
    name: str
    description: str | None
    display_order: int
    created_at: datetime


# ---------------------------------------------------------------------------
# Task Categories
# ---------------------------------------------------------------------------

class TaskCategoryCreate(BaseModel):
    name: str
    description: str | None = None
    display_order: int = 0
    icon: str | None = None
    color: str | None = None


class TaskCategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    display_order: int | None = None
    icon: str | None = None
    color: str | None = None


class TaskCategoryRead(BaseModel):
    id: int
    template_id: int
    name: str
    description: str | None
    display_order: int
    icon: str | None
    color: str | None
    created_at: datetime
    types: list[TaskTypeRead] = []


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

class TemplateCreate(BaseModel):
    name: str
    description: str | None = None


class TemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class TemplateRead(BaseModel):
    id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TemplateDetailRead(TemplateRead):
    """Full template with all children, used for GET /{template_id}."""
    statuses: list[StatusDefinitionRead] = []
    categories: list[TaskCategoryRead] = []