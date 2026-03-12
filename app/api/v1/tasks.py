from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import get_db
from app.models.db.task import TaskEnvironment, TaskPriority
from app.models.schemas.task import (
    TaskCommentCreate,
    TaskCommentRead,
    TaskCommentUpdate,
    TaskCreate,
    TaskDetailRead,
    TaskHistoryRead,
    TaskRead,
    TaskSummary,
    TaskUpdate,
)
from app.repositories import task_repo

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

@router.get("/", response_model=list[TaskRead])
def list_tasks(
    project_id: int = Query(..., description="Required: filter tasks by project"),
    category_id: int | None = None,
    type_id: int | None = None,
    status_id: int | None = None,
    component_id: int | None = None,
    assignee: str | None = None,
    priority: TaskPriority | None = None,
    environment: TaskEnvironment | None = None,
    db: Session = Depends(get_db),
):
    return task_repo.get_tasks(
        db,
        project_id=project_id,
        category_id=category_id,
        type_id=type_id,
        status_id=status_id,
        component_id=component_id,
        assignee=assignee,
        priority=priority,
        environment=environment,
    )


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    return task_repo.create_task(db, data)


@router.get("/summary", response_model=TaskSummary)
def get_task_summary(
    project_id: int = Query(..., description="Required: project to summarize"),
    environment: TaskEnvironment | None = Query(
        default=None,
        description="Optional: scope summary to a specific environment",
    ),
    db: Session = Depends(get_db),
):
    return task_repo.get_task_summary(db, project_id, environment=environment)


@router.get("/{task_id}", response_model=TaskDetailRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = task_repo.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    comments = task_repo.get_comments(db, task_id)
    recent_history = task_repo.get_recent_task_history(db, task_id, limit=10)

    return TaskDetailRead(
        **task.model_dump(),
        comments=comments,
        recent_history=recent_history,
    )


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):
    task = task_repo.update_task(db, task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    if not task_repo.delete_task(db, task_id):
        raise HTTPException(status_code=404, detail="Task not found")


# ---------------------------------------------------------------------------
# Task History
# ---------------------------------------------------------------------------

@router.get("/{task_id}/history", response_model=list[TaskHistoryRead])
def get_task_history(task_id: int, db: Session = Depends(get_db)):
    _require_task(db, task_id)
    return task_repo.get_task_history(db, task_id)


# ---------------------------------------------------------------------------
# Task Comments
# ---------------------------------------------------------------------------

@router.get("/{task_id}/comments", response_model=list[TaskCommentRead])
def list_comments(task_id: int, db: Session = Depends(get_db)):
    _require_task(db, task_id)
    return task_repo.get_comments(db, task_id)


@router.post(
    "/{task_id}/comments",
    response_model=TaskCommentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(task_id: int, data: TaskCommentCreate, db: Session = Depends(get_db)):
    _require_task(db, task_id)
    comment = task_repo.create_comment(db, task_id, data)
    if not comment:
        raise HTTPException(status_code=404, detail="Task not found")
    return comment


@router.patch("/{task_id}/comments/{comment_id}", response_model=TaskCommentRead)
def update_comment(
    task_id: int, comment_id: int, data: TaskCommentUpdate, db: Session = Depends(get_db)
):
    _require_task(db, task_id)
    comment = task_repo.update_comment(db, comment_id, data)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.delete("/{task_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(task_id: int, comment_id: int, db: Session = Depends(get_db)):
    _require_task(db, task_id)
    if not task_repo.delete_comment(db, comment_id):
        raise HTTPException(status_code=404, detail="Comment not found")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_task(db: Session, task_id: int) -> None:
    if not task_repo.get_task(db, task_id):
        raise HTTPException(status_code=404, detail="Task not found")