from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_db
from app.models.schemas.template import (
    StatusDefinitionCreate,
    StatusDefinitionRead,
    StatusDefinitionUpdate,
    StatusReorderRequest,
    TaskCategoryCreate,
    TaskCategoryRead,
    TaskCategoryUpdate,
    TaskTypeCreate,
    TaskTypeRead,
    TaskTypeUpdate,
    TemplateCreate,
    TemplateDetailRead,
    TemplateRead,
    TemplateUpdate,
)
from app.repositories import template_repo

router = APIRouter(prefix="/templates", tags=["Templates"])


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

@router.get("/", response_model=list[TemplateRead])
def list_templates(active_only: bool = True, db: Session = Depends(get_db)):
    return template_repo.get_templates(db, active_only=active_only)


@router.post("/", response_model=TemplateRead, status_code=status.HTTP_201_CREATED)
def create_template(data: TemplateCreate, db: Session = Depends(get_db)):
    return template_repo.create_template(db, data)


@router.get("/{template_id}", response_model=TemplateDetailRead)
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = template_repo.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.patch("/{template_id}", response_model=TemplateRead)
def update_template(template_id: int, data: TemplateUpdate, db: Session = Depends(get_db)):
    template = template_repo.update_template(db, template_id, data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.delete("/{template_id}", response_model=TemplateRead)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = template_repo.delete_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


# ---------------------------------------------------------------------------
# Statuses
# ---------------------------------------------------------------------------

@router.get("/{template_id}/statuses", response_model=list[StatusDefinitionRead])
def list_statuses(template_id: int, db: Session = Depends(get_db)):
    _require_template(db, template_id)
    return template_repo.get_statuses(db, template_id)


@router.post(
    "/{template_id}/statuses",
    response_model=StatusDefinitionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_status(template_id: int, data: StatusDefinitionCreate, db: Session = Depends(get_db)):
    _require_template(db, template_id)
    return template_repo.create_status(db, template_id, data)


@router.patch("/{template_id}/statuses/{status_id}", response_model=StatusDefinitionRead)
def update_status(template_id: int, status_id: int, data: StatusDefinitionUpdate, db: Session = Depends(get_db)):  # noqa: E501
    _require_template(db, template_id)
    result = template_repo.update_status(db, status_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Status not found")
    return result


@router.delete("/{template_id}/statuses/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_status(template_id: int, status_id: int, db: Session = Depends(get_db)):
    _require_template(db, template_id)
    if not template_repo.delete_status(db, status_id):
        raise HTTPException(
            status_code=409,
            detail="Cannot delete status: it is either not found or referenced by existing tasks",
        )


@router.put("/{template_id}/statuses/reorder", response_model=list[StatusDefinitionRead])
def reorder_statuses(template_id: int, data: StatusReorderRequest, db: Session = Depends(get_db)):
    _require_template(db, template_id)
    return template_repo.reorder_statuses(db, template_id, data.statuses)


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

@router.get("/{template_id}/categories", response_model=list[TaskCategoryRead])
def list_categories(template_id: int, db: Session = Depends(get_db)):
    _require_template(db, template_id)
    return template_repo.get_categories(db, template_id)


@router.post(
    "/{template_id}/categories",
    response_model=TaskCategoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_category(template_id: int, data: TaskCategoryCreate, db: Session = Depends(get_db)):
    _require_template(db, template_id)
    return template_repo.create_category(db, template_id, data)


@router.patch("/{template_id}/categories/{category_id}", response_model=TaskCategoryRead)
def update_category(
    template_id: int, category_id: int, data: TaskCategoryUpdate, db: Session = Depends(get_db)
):
    _require_template(db, template_id)
    result = template_repo.update_category(db, category_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Category not found")
    return result


@router.delete("/{template_id}/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(template_id: int, category_id: int, db: Session = Depends(get_db)):
    _require_template(db, template_id)
    if not template_repo.delete_category(db, category_id):
        raise HTTPException(
            status_code=409,
            detail="Cannot delete category: it is either not found or referenced by existing tasks",
        )


# ---------------------------------------------------------------------------
# Types (nested under categories)
# ---------------------------------------------------------------------------

@router.get(
    "/{template_id}/categories/{category_id}/types",
    response_model=list[TaskTypeRead],
)
def list_types(template_id: int, category_id: int, db: Session = Depends(get_db)):
    _require_template(db, template_id)
    _require_category(db, category_id)
    return template_repo.get_types(db, category_id)


@router.post(
    "/{template_id}/categories/{category_id}/types",
    response_model=TaskTypeRead,
    status_code=status.HTTP_201_CREATED,
)
def create_type(
    template_id: int, category_id: int, data: TaskTypeCreate, db: Session = Depends(get_db)
):
    _require_template(db, template_id)
    _require_category(db, category_id)
    return template_repo.create_type(db, category_id, data)


@router.patch(
    "/{template_id}/categories/{category_id}/types/{type_id}",
    response_model=TaskTypeRead,
)
def update_type(
    template_id: int, category_id: int, type_id: int, data: TaskTypeUpdate, db: Session = Depends(get_db)  # noqa: E501
):
    _require_template(db, template_id)
    result = template_repo.update_type(db, type_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Type not found")
    return result


@router.delete(
    "/{template_id}/categories/{category_id}/types/{type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_type(
    template_id: int, category_id: int, type_id: int, db: Session = Depends(get_db)
):
    _require_template(db, template_id)
    if not template_repo.delete_type(db, type_id):
        raise HTTPException(
            status_code=409,
            detail="Cannot delete type: it is either not found or referenced by existing tasks",
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_template(db: Session, template_id: int) -> None:
    if not template_repo.get_template(db, template_id):
        raise HTTPException(status_code=404, detail="Template not found")


def _require_category(db: Session, category_id: int) -> None:
    if not template_repo.get_category(db, category_id):
        raise HTTPException(status_code=404, detail="Category not found")