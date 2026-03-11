from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_db
from app.models.db.project import ProjectStatus
from app.models.schemas.project import (
    ProjectComponentCreate,
    ProjectComponentRead,
    ProjectComponentUpdate,
    ProjectCreate,
    ProjectDetailRead,
    ProjectRead,
    ProjectUpdate,
)
from app.repositories import project_repo

router = APIRouter(prefix="/projects", tags=["Projects"])


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

@router.get("/", response_model=list[ProjectRead])
def list_projects(
    status: ProjectStatus | None = None,
    template_id: int | None = None,
    owner: str | None = None,
    db: Session = Depends(get_db),
):
    return project_repo.get_projects(db, status=status, template_id=template_id, owner=owner)


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    return project_repo.create_project(db, data)


@router.get("/{project_id}", response_model=ProjectDetailRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = project_repo.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    task_count, tasks_by_status = project_repo.get_project_task_summary(db, project_id)

    return ProjectDetailRead(
        **project.model_dump(),
        components=[c.model_dump() for c in project.components],
        task_count=task_count,
        tasks_by_status=tasks_by_status,
    )


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = project_repo.update_project(db, project_id, data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}", response_model=ProjectRead)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Archives the project rather than hard-deleting it."""
    project = project_repo.archive_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------

@router.get("/{project_id}/components", response_model=list[ProjectComponentRead])
def list_components(project_id: int, db: Session = Depends(get_db)):
    _require_project(db, project_id)
    return project_repo.get_components(db, project_id)


@router.post(
    "/{project_id}/components",
    response_model=ProjectComponentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_component(project_id: int, data: ProjectComponentCreate, db: Session = Depends(get_db)):
    _require_project(db, project_id)
    return project_repo.create_component(db, project_id, data)


@router.patch("/{project_id}/components/{component_id}", response_model=ProjectComponentRead)
def update_component(
    project_id: int, component_id: int, data: ProjectComponentUpdate, db: Session = Depends(get_db)
):
    _require_project(db, project_id)
    result = project_repo.update_component(db, component_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Component not found")
    return result


@router.delete("/{project_id}/components/{component_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_component(project_id: int, component_id: int, db: Session = Depends(get_db)):
    _require_project(db, project_id)
    if not project_repo.delete_component(db, component_id):
        raise HTTPException(
            status_code=409,
            detail="Cannot delete component: it is either not found or referenced by existing tasks",  # noqa: E501
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_project(db: Session, project_id: int) -> None:
    if not project_repo.get_project(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found")