import logging
from datetime import datetime

from sqlmodel import Session, func, select

from app.models.db.project import ProjectComponent
from app.models.db.task import Task, TaskComment, TaskEnvironment, TaskHistory, TaskPriority
from app.models.db.template import StatusDefinition, TaskCategory
from app.models.schemas.task import (
    TaskCommentCreate,
    TaskCommentUpdate,
    TaskCreate,
    TaskUpdate,
)
from app.repositories import template_repo

logger = logging.getLogger(__name__)

# Fields that are tracked in task_history when updated
AUDITED_FIELDS = {
    "category_id", "type_id", "status_id", "component_id",
    "title", "description", "assignee", "priority", "environment",
    "start_date", "due_date",
}


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def get_tasks(
    session: Session,
    *,
    project_id: int,
    category_id: int | None = None,
    type_id: int | None = None,
    status_id: int | None = None,
    component_id: int | None = None,
    assignee: str | None = None,
    priority: TaskPriority | None = None,
    environment: TaskEnvironment | None = None,
) -> list[Task]:
    stmt = select(Task).where(Task.project_id == project_id)
    if category_id is not None:
        stmt = stmt.where(Task.category_id == category_id)
    if type_id is not None:
        stmt = stmt.where(Task.type_id == type_id)
    if status_id is not None:
        stmt = stmt.where(Task.status_id == status_id)
    if component_id is not None:
        stmt = stmt.where(Task.component_id == component_id)
    if assignee is not None:
        stmt = stmt.where(Task.assignee == assignee)
    if priority is not None:
        stmt = stmt.where(Task.priority == priority)
    if environment is not None:
        stmt = stmt.where(Task.environment == environment)
    stmt = stmt.order_by(Task.created_at.desc())
    return list(session.exec(stmt).all())


def get_task(session: Session, task_id: int) -> Task | None:
    return session.get(Task, task_id)


def create_task(session: Session, data: TaskCreate) -> Task:
    task_data = data.model_dump()

    # Resolve default status if not provided
    if task_data.get("status_id") is None:
        from app.models.db.project import Project

        project = session.get(Project, data.project_id)
        if project:
            default_status = template_repo.get_default_status(session, project.template_id)
            if default_status:
                task_data["status_id"] = default_status.id

    task = Task(**task_data)
    session.add(task)
    session.commit()
    session.refresh(task)
    logger.info("Created task id=%s title='%s' in project_id=%s", task.id, task.title, task.project_id)  # noqa: E501
    return task


def update_task(session: Session, task_id: int, data: TaskUpdate) -> Task | None:
    """Update a task and auto-write history entries for every changed field."""
    task = session.get(Task, task_id)
    if not task:
        return None

    changed_by = data.changed_by
    updates = data.model_dump(exclude_unset=True, exclude={"changed_by"})
    now = datetime.utcnow()

    for field, new_value in updates.items():
        old_value = getattr(task, field)

        # Normalize for comparison (enums, dates, etc.)
        old_str = str(old_value) if old_value is not None else None
        new_str = str(new_value) if new_value is not None else None

        if old_str != new_str:
            # Write audit entry
            if field in AUDITED_FIELDS:
                history = TaskHistory(
                    task_id=task_id,
                    field_changed=field,
                    old_value=old_str,
                    new_value=new_str,
                    changed_by=changed_by,
                    changed_at=now,
                )
                session.add(history)

            setattr(task, field, new_value)

    # Auto-set completed_at when status becomes terminal
    if "status_id" in updates:
        status = session.get(StatusDefinition, updates["status_id"])
        if status and status.is_terminal:
            task.completed_at = now
        elif status and not status.is_terminal:
            task.completed_at = None

    task.updated_at = now
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def delete_task(session: Session, task_id: int) -> bool:
    task = session.get(Task, task_id)
    if not task:
        return False
    # Delete related comments and history first
    for comment in task.comments:
        session.delete(comment)
    for entry in task.history:
        session.delete(entry)
    session.delete(task)
    session.commit()
    return True


# ---------------------------------------------------------------------------
# Task History
# ---------------------------------------------------------------------------

def get_task_history(session: Session, task_id: int) -> list[TaskHistory]:
    stmt = (
        select(TaskHistory)
        .where(TaskHistory.task_id == task_id)
        .order_by(TaskHistory.changed_at.desc())
    )
    return list(session.exec(stmt).all())


def get_recent_task_history(session: Session, task_id: int, limit: int = 10) -> list[TaskHistory]:
    stmt = (
        select(TaskHistory)
        .where(TaskHistory.task_id == task_id)
        .order_by(TaskHistory.changed_at.desc())
        .limit(limit)
    )
    return list(session.exec(stmt).all())


# ---------------------------------------------------------------------------
# Task Comments
# ---------------------------------------------------------------------------

def get_comments(session: Session, task_id: int) -> list[TaskComment]:
    stmt = (
        select(TaskComment)
        .where(TaskComment.task_id == task_id)
        .order_by(TaskComment.created_at.asc())
    )
    return list(session.exec(stmt).all())


def create_comment(session: Session, task_id: int, data: TaskCommentCreate) -> TaskComment | None:
    task = session.get(Task, task_id)
    if not task:
        return None
    comment = TaskComment(task_id=task_id, **data.model_dump())
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


def update_comment(session: Session, comment_id: int, data: TaskCommentUpdate) -> TaskComment | None:  # noqa: E501
    comment = session.get(TaskComment, comment_id)
    if not comment:
        return None
    comment.body = data.body
    comment.updated_at = datetime.utcnow()
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


def delete_comment(session: Session, comment_id: int) -> bool:
    comment = session.get(TaskComment, comment_id)
    if not comment:
        return False
    session.delete(comment)
    session.commit()
    return True


# ---------------------------------------------------------------------------
# Task Summary
# ---------------------------------------------------------------------------

def get_task_summary(
    session: Session,
    project_id: int,
    *,
    environment: TaskEnvironment | None = None,
) -> dict:
    """Aggregate task counts by status, category, component, priority, and environment.

    When *environment* is provided the counts are scoped to that environment only.
    """

    def _base_where(stmt):
        """Apply shared project (and optional environment) filter."""
        stmt = stmt.where(Task.project_id == project_id)
        if environment is not None:
            stmt = stmt.where(Task.environment == environment)
        return stmt

    # By status
    status_stmt = _base_where(
        select(StatusDefinition.name, func.count(Task.id))
        .join(StatusDefinition, Task.status_id == StatusDefinition.id)
    ).group_by(StatusDefinition.name)
    by_status = {name: count for name, count in session.exec(status_stmt).all()}

    # By category
    cat_stmt = _base_where(
        select(TaskCategory.name, func.count(Task.id))
        .join(TaskCategory, Task.category_id == TaskCategory.id)
    ).group_by(TaskCategory.name)
    by_category = {name: count for name, count in session.exec(cat_stmt).all()}

    # By component (tasks without a component are grouped as "Unassigned")
    comp_stmt = _base_where(
        select(ProjectComponent.name, func.count(Task.id))
        .join(ProjectComponent, Task.component_id == ProjectComponent.id)
    ).where(Task.component_id.isnot(None)).group_by(ProjectComponent.name)
    by_component = {name: count for name, count in session.exec(comp_stmt).all()}

    # Count tasks with no component
    unassigned_stmt = _base_where(
        select(func.count(Task.id))
    ).where(Task.component_id.is_(None))
    unassigned = session.exec(unassigned_stmt).one()
    if unassigned:
        by_component["Unassigned"] = unassigned

    # By priority
    priority_stmt = _base_where(
        select(Task.priority, func.count(Task.id))
    ).group_by(Task.priority)
    by_priority = {str(priority): count for priority, count in session.exec(priority_stmt).all()}

    # By environment
    env_stmt = (
        select(Task.environment, func.count(Task.id))
        .where(Task.project_id == project_id)
        .group_by(Task.environment)
    )
    by_environment = {}
    for env_val, count in session.exec(env_stmt).all():
        label = str(env_val) if env_val is not None else "Unassigned"
        by_environment[label] = count

    total = sum(by_status.values())

    return {
        "total": total,
        "by_status": by_status,
        "by_category": by_category,
        "by_component": by_component,
        "by_priority": by_priority,
        "by_environment": by_environment,
    }