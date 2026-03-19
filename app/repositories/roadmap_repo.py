"""
Roadmap summary repository.

Location: app/repositories/roadmap_repo.py

Queries the tasks table joined with template metadata to produce the
executive-level roadmap summary grouped by category (phase).
"""

from sqlalchemy import func  # noqa: F401
from sqlmodel import Session, select

from app.models.db.roadmap import (
    ProjectComponent,
    StatusDefinition,
    Task,
    TaskCategory,
    TaskEnvironment,
    TaskType,
)
from app.models.schemas.roadmap import (
    RoadmapPhaseRead,
    RoadmapSummaryRead,
    RoadmapTaskRead,
    StatusBreakdown,
)

# ---------------------------------------------------------------------------
# Status name → StatusBreakdown field mapping
# ---------------------------------------------------------------------------

_STATUS_KEY = {
    "Not Started": "not_started",
    "In Progress": "in_progress",
    "In Review":   "in_review",
    "Blocked":     "blocked",
    "Complete":    "complete",
}


def _increment_status(breakdown: dict, status_name: str) -> None:
    """Increment the appropriate counter in a StatusBreakdown kwargs dict."""
    key = _STATUS_KEY.get(status_name)
    if key:
        breakdown[key] = breakdown.get(key, 0) + 1


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_roadmap_summary(
    db: Session,
    project_id: int,
    project_name: str,
    template_id: int,
    *,
    environment: TaskEnvironment | None = None,
) -> RoadmapSummaryRead:
    """
    Build the full roadmap summary for a project, optionally scoped to an
    environment.  Returns phases ordered by category display_order with
    tasks nested inside each phase.
    """

    # -- Build the query --------------------------------------------------------
    stmt = (
        select(
            Task.id,
            Task.title,
            Task.description,
            Task.priority,
            Task.environment,
            Task.start_date,
            Task.due_date,
            Task.completed_at,
            StatusDefinition.name.label("status_name"),            # type: ignore[attr-defined]
            TaskCategory.id.label("category_id"),                  # type: ignore[attr-defined]
            TaskCategory.name.label("category_name"),              # type: ignore[attr-defined]
            TaskCategory.description.label("category_description"),# type: ignore[attr-defined]
            TaskCategory.display_order.label("category_order"),    # type: ignore[attr-defined]
            TaskCategory.icon.label("category_icon"),              # type: ignore[attr-defined]
            TaskCategory.color.label("category_color"),            # type: ignore[attr-defined]
            TaskType.name.label("type_name"),                      # type: ignore[attr-defined]
            ProjectComponent.name.label("component_name"),         # type: ignore[attr-defined]
        )
        .join(StatusDefinition, Task.status_id == StatusDefinition.id)
        .join(TaskCategory, Task.category_id == TaskCategory.id)
        .outerjoin(TaskType, Task.type_id == TaskType.id)
        .outerjoin(ProjectComponent, Task.component_id == ProjectComponent.id)
        .where(Task.project_id == project_id)
        .order_by(TaskCategory.display_order, Task.start_date, Task.id)
    )

    if environment is not None:
        stmt = stmt.where(Task.environment == environment)

    rows = db.exec(stmt).all()

    # -- Accumulate phases keyed by category_id ---------------------------------
    phases_map: dict[int, dict] = {}
    overall_counts: dict[str, int] = {}

    for row in rows:
        cat_id = row.category_id

        if cat_id not in phases_map:
            phases_map[cat_id] = {
                "category_id": cat_id,
                "name": row.category_name,
                "description": row.category_description,
                "display_order": row.category_order,
                "icon": row.category_icon,
                "color": row.category_color,
                "status_counts": {},
                "starts": [],
                "dues": [],
                "tasks": [],
            }

        phase = phases_map[cat_id]

        # Build task read model
        task = RoadmapTaskRead(
            id=row.id,
            title=row.title,
            description=row.description,
            type_name=row.type_name,
            component_name=row.component_name,
            status=row.status_name,
            priority=row.priority,
            environment=row.environment,
            start_date=str(row.start_date) if row.start_date else None,
            due_date=str(row.due_date) if row.due_date else None,
            completed_at=str(row.completed_at) if row.completed_at else None,
        )
        phase["tasks"].append(task)

        # Track status counts per phase and overall
        _increment_status(phase["status_counts"], row.status_name)
        _increment_status(overall_counts, row.status_name)

        # Track date ranges
        if row.start_date:
            phase["starts"].append(str(row.start_date))
        if row.due_date:
            phase["dues"].append(str(row.due_date))

    # -- Assemble phase response objects ----------------------------------------
    phases: list[RoadmapPhaseRead] = []
    for phase_data in sorted(phases_map.values(), key=lambda p: p["display_order"]):
        phases.append(
            RoadmapPhaseRead(
                category_id=phase_data["category_id"],
                name=phase_data["name"],
                description=phase_data["description"],
                display_order=phase_data["display_order"],
                icon=phase_data["icon"],
                color=phase_data["color"],
                progress=StatusBreakdown(**phase_data["status_counts"]),
                earliest_start=min(phase_data["starts"]) if phase_data["starts"] else None,
                latest_due=max(phase_data["dues"]) if phase_data["dues"] else None,
                tasks=phase_data["tasks"],
            )
        )

    return RoadmapSummaryRead(
        project_id=project_id,
        project_name=project_name,
        template_id=template_id,
        progress=StatusBreakdown(**overall_counts),
        phases=phases,
    )