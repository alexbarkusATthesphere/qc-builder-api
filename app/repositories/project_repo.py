import logging
from datetime import datetime

from sqlmodel import Session, func, select

from app.models.db.project import Project, ProjectComponent, ProjectStatus
from app.models.db.task import Task
from app.models.db.template import StatusDefinition
from app.models.schemas.project import (
    ProjectComponentCreate,
    ProjectComponentUpdate,
    ProjectCreate,
    ProjectUpdate,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def get_projects(
    session: Session,
    *,
    status: ProjectStatus | None = None,
    template_id: int | None = None,
    owner: str | None = None,
) -> list[Project]:
    stmt = select(Project)
    if status:
        stmt = stmt.where(Project.status == status)
    if template_id:
        stmt = stmt.where(Project.template_id == template_id)
    if owner:
        stmt = stmt.where(Project.owner == owner)
    stmt = stmt.order_by(Project.updated_at.desc())
    return list(session.exec(stmt).all())


def get_project(session: Session, project_id: int) -> Project | None:
    return session.get(Project, project_id)


def get_project_task_summary(session: Session, project_id: int) -> tuple[int, dict[str, int]]:
    """Return (total_count, {status_name: count}) for a project's tasks."""
    stmt = (
        select(StatusDefinition.name, func.count(Task.id))
        .join(StatusDefinition, Task.status_id == StatusDefinition.id)
        .where(Task.project_id == project_id)
        .group_by(StatusDefinition.name)
    )
    rows = session.exec(stmt).all()
    by_status = {name: count for name, count in rows}
    total = sum(by_status.values())
    return total, by_status


def create_project(session: Session, data: ProjectCreate) -> Project:
    project = Project(**data.model_dump())
    session.add(project)
    session.commit()
    session.refresh(project)
    logger.info("Created project id=%s name='%s'", project.id, project.name)
    return project


def update_project(session: Session, project_id: int, data: ProjectUpdate) -> Project | None:
    project = session.get(Project, project_id)
    if not project:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    project.updated_at = datetime.utcnow()
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def archive_project(session: Session, project_id: int) -> Project | None:
    project = session.get(Project, project_id)
    if not project:
        return None
    project.status = ProjectStatus.ARCHIVED
    project.updated_at = datetime.utcnow()
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


# ---------------------------------------------------------------------------
# Project Components
# ---------------------------------------------------------------------------

def get_components(session: Session, project_id: int) -> list[ProjectComponent]:
    stmt = (
        select(ProjectComponent)
        .where(ProjectComponent.project_id == project_id)
        .order_by(ProjectComponent.display_order)
    )
    return list(session.exec(stmt).all())


def create_component(session: Session, project_id: int, data: ProjectComponentCreate) -> ProjectComponent:  # noqa: E501
    component = ProjectComponent(project_id=project_id, **data.model_dump())
    session.add(component)
    session.commit()
    session.refresh(component)
    logger.info("Created component id=%s name='%s' for project_id=%s", component.id, component.name, project_id)  # noqa: E501
    return component


def update_component(session: Session, component_id: int, data: ProjectComponentUpdate) -> ProjectComponent | None:  # noqa: E501
    component = session.get(ProjectComponent, component_id)
    if not component:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(component, key, value)
    session.add(component)
    session.commit()
    session.refresh(component)
    return component


def delete_component(session: Session, component_id: int) -> bool:
    """Delete a component. Returns False if tasks reference it."""
    component = session.get(ProjectComponent, component_id)
    if not component:
        return False
    count = session.exec(select(Task).where(Task.component_id == component_id)).first()
    if count:
        return False
    session.delete(component)
    session.commit()
    return True