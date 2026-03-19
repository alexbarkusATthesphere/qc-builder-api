"""
Location: app/api/v1/router.py
"""

from fastapi import APIRouter

from app.api.v1.projects import router as projects_router
from app.api.v1.roadmap import router as roadmap_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.templates import router as templates_router

router = APIRouter()

router.include_router(templates_router)
router.include_router(projects_router)
router.include_router(tasks_router)
router.include_router(roadmap_router)