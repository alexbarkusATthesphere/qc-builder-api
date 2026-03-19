"""
Executive Roadmap router.

Location: app/api/v1/roadmap.py

Provides a read-only, executive-level view of a project's tasks grouped
by roadmap phase (template category) with roll-up progress stats.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.api.deps import get_db
from app.models.db.task import TaskEnvironment
from app.models.schemas.roadmap import RoadmapSummaryRead
from app.repositories import project_repo, roadmap_repo

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])


@router.get(
    "/projects/{project_id}/summary",
    response_model=RoadmapSummaryRead,
    summary="Executive roadmap summary",
    description=(
        "Returns a project's tasks grouped by roadmap phase (category) with "
        "status breakdowns, percent-complete, date ranges, and nested task "
        "details.  Optionally scoped to a single environment."
    ),
)
def get_roadmap_summary(
    project_id: int,
    environment: TaskEnvironment | None = Query(
        default=None,
        description="Optional: scope the summary to DEV, TEST, or PROD",
    ),
    db: Session = Depends(get_db),
):
    project = project_repo.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return roadmap_repo.get_roadmap_summary(
        db,
        project_id=project.id,
        project_name=project.name,
        template_id=project.template_id,
        environment=environment,
    )