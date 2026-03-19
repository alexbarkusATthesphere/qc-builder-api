"""
Roadmap summary response schemas.

Location: app/models/schemas/roadmap.py
"""

from pydantic import BaseModel, computed_field

# ---------------------------------------------------------------------------
# Phase-level task (slimmed-down read model for executive view)
# ---------------------------------------------------------------------------

class RoadmapTaskRead(BaseModel):
    id: int
    title: str
    description: str | None = None
    type_name: str | None = None
    component_name: str | None = None
    status: str
    priority: str
    environment: str | None = None
    start_date: str | None = None
    due_date: str | None = None
    completed_at: str | None = None


# ---------------------------------------------------------------------------
# Status breakdown (reused at both phase and overall level)
# ---------------------------------------------------------------------------

class StatusBreakdown(BaseModel):
    complete: int = 0
    in_progress: int = 0
    in_review: int = 0
    blocked: int = 0
    not_started: int = 0

    @computed_field
    @property
    def total(self) -> int:
        return (
            self.complete
            + self.in_progress
            + self.in_review
            + self.blocked
            + self.not_started
        )

    @computed_field
    @property
    def percent_complete(self) -> float:
        if self.total == 0:
            return 0.0
        return round((self.complete / self.total) * 100, 1)


# ---------------------------------------------------------------------------
# Single roadmap phase (one of the four categories)
# ---------------------------------------------------------------------------

class RoadmapPhaseRead(BaseModel):
    category_id: int
    name: str
    description: str | None = None
    display_order: int
    icon: str | None = None
    color: str | None = None
    progress: StatusBreakdown
    earliest_start: str | None = None
    latest_due: str | None = None
    tasks: list[RoadmapTaskRead]


# ---------------------------------------------------------------------------
# Top-level roadmap summary response
# ---------------------------------------------------------------------------

class RoadmapSummaryRead(BaseModel):
    project_id: int
    project_name: str
    template_id: int
    progress: StatusBreakdown
    phases: list[RoadmapPhaseRead]