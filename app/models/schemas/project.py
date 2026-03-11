from datetime import date, datetime

from pydantic import BaseModel

from app.models.db.project import ProjectStatus

# ---------------------------------------------------------------------------
# Project Components
# ---------------------------------------------------------------------------

class ProjectComponentCreate(BaseModel):
    name: str
    description: str | None = None
    display_order: int = 0


class ProjectComponentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    display_order: int | None = None


class ProjectComponentRead(BaseModel):
    id: int
    project_id: int
    name: str
    description: str | None
    display_order: int
    created_at: datetime


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

class ProjectCreate(BaseModel):
    template_id: int
    name: str
    description: str | None = None
    owner: str | None = None
    status: ProjectStatus = ProjectStatus.ACTIVE
    start_date: date | None = None
    target_end_date: date | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    owner: str | None = None
    status: ProjectStatus | None = None
    start_date: date | None = None
    target_end_date: date | None = None


class ProjectRead(BaseModel):
    id: int
    template_id: int
    name: str
    description: str | None
    owner: str | None
    status: ProjectStatus
    start_date: date | None
    target_end_date: date | None
    created_at: datetime
    updated_at: datetime


class ProjectDetailRead(ProjectRead):
    """Project with components and task summary counts."""
    components: list[ProjectComponentRead] = []
    task_count: int = 0
    tasks_by_status: dict[str, int] = {}