"""
Roadmap domain models.

Location: app/models/db/roadmap.py

The roadmap domain is a **read-only aggregation view** over the existing
task, status, category, type, and component tables.  It does not define
its own database table — all data lives in :mod:`app.models.db.task`,
:mod:`app.models.db.template`, and :mod:`app.models.db.project`.

This module re-exports the ORM models used by the roadmap repository
so that the import pattern stays consistent across the codebase:

    from app.models.db.roadmap import Task, TaskCategory, ...
"""

from app.models.db.project import Project, ProjectComponent
from app.models.db.task import Task, TaskEnvironment
from app.models.db.template import StatusDefinition, TaskCategory, TaskType

__all__ = [
    "Project",
    "ProjectComponent",
    "StatusDefinition",
    "Task",
    "TaskCategory",
    "TaskEnvironment",
    "TaskType",
]