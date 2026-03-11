import logging

from sqlmodel import Session, select

from app.models.db.template import (
    StatusDefinition,
    TaskCategory,
    TaskType,
    Template,
)
from app.models.schemas.template import (
    StatusDefinitionCreate,
    StatusDefinitionUpdate,
    StatusReorderItem,
    TaskCategoryCreate,
    TaskCategoryUpdate,
    TaskTypeCreate,
    TaskTypeUpdate,
    TemplateCreate,
    TemplateUpdate,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def get_templates(session: Session, *, active_only: bool = True) -> list[Template]:
    stmt = select(Template)
    if active_only:
        stmt = stmt.where(Template.is_active == True)  # noqa: E712
    return list(session.exec(stmt).all())


def get_template(session: Session, template_id: int) -> Template | None:
    return session.get(Template, template_id)


def create_template(session: Session, data: TemplateCreate) -> Template:
    template = Template(**data.model_dump())
    session.add(template)
    session.commit()
    session.refresh(template)
    logger.info("Created template id=%s name='%s'", template.id, template.name)
    return template


def update_template(session: Session, template_id: int, data: TemplateUpdate) -> Template | None:
    template = session.get(Template, template_id)
    if not template:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(template, key, value)
    session.add(template)
    session.commit()
    session.refresh(template)
    return template


def delete_template(session: Session, template_id: int) -> Template | None:
    """Soft-delete by setting is_active=False."""
    template = session.get(Template, template_id)
    if not template:
        return None
    template.is_active = False
    session.add(template)
    session.commit()
    session.refresh(template)
    return template


# ---------------------------------------------------------------------------
# Status Definitions
# ---------------------------------------------------------------------------

def get_statuses(session: Session, template_id: int) -> list[StatusDefinition]:
    stmt = (
        select(StatusDefinition)
        .where(StatusDefinition.template_id == template_id)
        .order_by(StatusDefinition.display_order)
    )
    return list(session.exec(stmt).all())


def create_status(session: Session, template_id: int, data: StatusDefinitionCreate) -> StatusDefinition:  # noqa: E501
    status = StatusDefinition(template_id=template_id, **data.model_dump())
    session.add(status)
    session.commit()
    session.refresh(status)
    logger.info("Created status id=%s name='%s' for template_id=%s", status.id, status.name, template_id)  # noqa: E501
    return status


def update_status(session: Session, status_id: int, data: StatusDefinitionUpdate) -> StatusDefinition | None:  # noqa: E501
    status = session.get(StatusDefinition, status_id)
    if not status:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(status, key, value)
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


def delete_status(session: Session, status_id: int) -> bool:
    """Delete a status. Returns False if tasks reference it."""
    from app.models.db.task import Task

    status = session.get(StatusDefinition, status_id)
    if not status:
        return False
    # Check for referencing tasks
    count = session.exec(select(Task).where(Task.status_id == status_id)).first()
    if count:
        return False
    session.delete(status)
    session.commit()
    return True


def reorder_statuses(session: Session, template_id: int, items: list[StatusReorderItem]) -> list[StatusDefinition]:  # noqa: E501
    for item in items:
        status = session.get(StatusDefinition, item.id)
        if status and status.template_id == template_id:
            status.display_order = item.display_order
            session.add(status)
    session.commit()
    return get_statuses(session, template_id)


def get_default_status(session: Session, template_id: int) -> StatusDefinition | None:
    stmt = select(StatusDefinition).where(
        StatusDefinition.template_id == template_id,
        StatusDefinition.is_default == True,  # noqa: E712
    )
    return session.exec(stmt).first()


# ---------------------------------------------------------------------------
# Task Categories
# ---------------------------------------------------------------------------

def get_categories(session: Session, template_id: int) -> list[TaskCategory]:
    stmt = (
        select(TaskCategory)
        .where(TaskCategory.template_id == template_id)
        .order_by(TaskCategory.display_order)
    )
    return list(session.exec(stmt).all())


def get_category(session: Session, category_id: int) -> TaskCategory | None:
    return session.get(TaskCategory, category_id)


def create_category(session: Session, template_id: int, data: TaskCategoryCreate) -> TaskCategory:
    category = TaskCategory(template_id=template_id, **data.model_dump())
    session.add(category)
    session.commit()
    session.refresh(category)
    logger.info("Created category id=%s name='%s' for template_id=%s", category.id, category.name, template_id)  # noqa: E501
    return category


def update_category(session: Session, category_id: int, data: TaskCategoryUpdate) -> TaskCategory | None:  # noqa: E501
    category = session.get(TaskCategory, category_id)
    if not category:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def delete_category(session: Session, category_id: int) -> bool:
    """Delete a category. Returns False if tasks reference it."""
    from app.models.db.task import Task

    category = session.get(TaskCategory, category_id)
    if not category:
        return False
    count = session.exec(select(Task).where(Task.category_id == category_id)).first()
    if count:
        return False
    session.delete(category)
    session.commit()
    return True


# ---------------------------------------------------------------------------
# Task Types
# ---------------------------------------------------------------------------

def get_types(session: Session, category_id: int) -> list[TaskType]:
    stmt = (
        select(TaskType)
        .where(TaskType.category_id == category_id)
        .order_by(TaskType.display_order)
    )
    return list(session.exec(stmt).all())


def create_type(session: Session, category_id: int, data: TaskTypeCreate) -> TaskType:
    task_type = TaskType(category_id=category_id, **data.model_dump())
    session.add(task_type)
    session.commit()
    session.refresh(task_type)
    logger.info("Created type id=%s name='%s' for category_id=%s", task_type.id, task_type.name, category_id)  # noqa: E501
    return task_type


def update_type(session: Session, type_id: int, data: TaskTypeUpdate) -> TaskType | None:
    task_type = session.get(TaskType, type_id)
    if not task_type:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(task_type, key, value)
    session.add(task_type)
    session.commit()
    session.refresh(task_type)
    return task_type


def delete_type(session: Session, type_id: int) -> bool:
    """Delete a type. Returns False if tasks reference it."""
    from app.models.db.task import Task

    task_type = session.get(TaskType, type_id)
    if not task_type:
        return False
    count = session.exec(select(Task).where(Task.type_id == type_id)).first()
    if count:
        return False
    session.delete(task_type)
    session.commit()
    return True