"""Import all ORM models so SQLModel registers them and forward refs resolve."""

from app.models.db.project import Project, ProjectComponent  # noqa: F401
from app.models.db.roadmap import *  # noqa: F401, F403
from app.models.db.task import Task, TaskComment, TaskHistory  # noqa: F401
from app.models.db.template import (  # noqa: F401
    StatusDefinition,
    TaskCategory,
    TaskType,
    Template,
)

# Rebuild models to resolve forward references across modules
Template.model_rebuild()
Project.model_rebuild()
Task.model_rebuild()