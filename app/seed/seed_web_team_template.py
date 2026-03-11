"""Seed the database with the Web Development template and a sample SWIKI project.

Usage:
    1. Start the API once so init_db() creates all tables.
    2. Run this script:

        python -m app.seed.seed_web_team_template

    The script is idempotent-ish: it checks for the template by name
    before inserting. If "Web Development" already exists, it skips.
"""

import logging
import sys
from pathlib import Path

from sqlmodel import Session, select

# Ensure project root is on sys.path when running as a module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.core.database import engine, init_db
from app.core.logging import setup_logging
from app.models.db import (  # noqa: F401 — triggers model registration
    Project,
    ProjectComponent,
    StatusDefinition,
    Task,
    TaskCategory,
    TaskType,
    Template,
)
from app.models.db.project import ProjectStatus
from app.models.db.task import TaskPriority

logger = logging.getLogger(__name__)


def seed() -> None:
    setup_logging()

    # Create tables if they don't exist (same as app startup)
    init_db()

    with Session(engine) as session:
        # Check if already seeded
        existing = session.exec(
            select(Template).where(Template.name == "Web Development")
        ).first()
        if existing:
            logger.info("Template 'Web Development' already exists (id=%s). Skipping seed.", existing.id)
            return

        # =================================================================
        # Template
        # =================================================================
        template = Template(
            name="Web Development",
            description=(
                "Template for web development teams managing frontend, backend, "
                "and data pipeline work alongside cross-team communication and documentation."
            ),
        )
        session.add(template)
        session.flush()  # Get template.id

        logger.info("Created template: %s (id=%s)", template.name, template.id)

        # =================================================================
        # Status Definitions
        # =================================================================
        statuses_data = [
            {"name": "Not Started", "color": "#6B7280", "display_order": 1, "is_default": True,  "is_terminal": False},
            {"name": "In Progress", "color": "#3B82F6", "display_order": 2, "is_default": False, "is_terminal": False},
            {"name": "In Review",   "color": "#8B5CF6", "display_order": 3, "is_default": False, "is_terminal": False},
            {"name": "Blocked",     "color": "#EF4444", "display_order": 4, "is_default": False, "is_terminal": False},
            {"name": "Complete",    "color": "#10B981", "display_order": 5, "is_default": False, "is_terminal": True},
        ]

        status_map: dict[str, StatusDefinition] = {}
        for s in statuses_data:
            status = StatusDefinition(template_id=template.id, **s)
            session.add(status)
            session.flush()
            status_map[status.name] = status

        logger.info("Created %d statuses", len(status_map))

        # =================================================================
        # Task Categories and Types
        # =================================================================
        categories_config = {
            "Development": {
                "description": "Code-level work: new features, pipelines, routes, bug fixes, and refactors.",
                "display_order": 1,
                "icon": "code",
                "color": "#3B82F6",
                "types": [
                    ("New ETL Pipeline",     "Build a new ETL pipeline or add a new pipeline to an existing family."),
                    ("New API Route",        "Add a new endpoint or domain router to the API."),
                    ("New Frontend Feature", "Build a new page, component, or feature in the Angular frontend."),
                    ("Bug Fix",             "Fix a defect in existing functionality."),
                    ("Refactor",            "Restructure existing code without changing behavior."),
                    ("Infrastructure",      "DevOps, CI/CD, Docker, VM setup, environment configuration."),
                ],
            },
            "Communication": {
                "description": "Cross-team coordination, stakeholder updates, and access requests.",
                "display_order": 2,
                "icon": "message-square",
                "color": "#F59E0B",
                "types": [
                    ("Cross-Team Request",          "Request or coordinate work with another team."),
                    ("Stakeholder Update",          "Provide a status update or demo to stakeholders."),
                    ("Access / Provisioning Request", "Request access, credentials, licenses, or infrastructure."),
                    ("Vendor Coordination",         "Coordinate with an external vendor or contractor."),
                ],
            },
            "Documentation": {
                "description": "Technical documentation, playbooks, READMEs, and reference material.",
                "display_order": 3,
                "icon": "file-text",
                "color": "#10B981",
                "types": [
                    ("README",         "Repository or project README file."),
                    ("Technical Doc",  "Architecture docs, design docs, or technical specifications."),
                    ("Playbook",       "Operational playbook or runbook for a process."),
                    ("Program Document", "HSE program, policy, or compliance document."),
                    ("Runbook",        "Step-by-step operational procedure for incident response or maintenance."),
                ],
            },
        }

        category_map: dict[str, TaskCategory] = {}
        type_map: dict[str, TaskType] = {}

        for cat_name, cat_config in categories_config.items():
            types_data = cat_config.pop("types")
            category = TaskCategory(template_id=template.id, name=cat_name, **cat_config)
            session.add(category)
            session.flush()
            category_map[cat_name] = category

            for order, (type_name, type_desc) in enumerate(types_data, start=1):
                task_type = TaskType(
                    category_id=category.id,
                    name=type_name,
                    description=type_desc,
                    display_order=order,
                )
                session.add(task_type)
                session.flush()
                type_map[type_name] = task_type

        logger.info("Created %d categories with %d types", len(category_map), len(type_map))

        # =================================================================
        # Project: SWIKI
        # =================================================================
        project = Project(
            template_id=template.id,
            name="SWIKI - Internal Knowledge Base",
            description=(
                "Multi-stakeholder internal knowledge base and operations portal for The Sphere. "
                "Includes ETL pipelines for data ingestion, a FastAPI backend, and an Angular frontend "
                "with role-gated portals for executives, security, HSE, and developers."
            ),
            owner="Web Development Team",
            status=ProjectStatus.ACTIVE,
        )
        session.add(project)
        session.flush()

        logger.info("Created project: %s (id=%s)", project.name, project.id)

        # =================================================================
        # Project Components
        # =================================================================
        components_data = [
            ("ETL Pipelines", "Python ETL pipelines for ingesting data from Workforce, TeamUp, Tableau, and Excel sources."),
            ("API",           "FastAPI REST backend serving 11 domain routers for the SWIKI portal."),
            ("Frontend",      "Angular 21 SPA with stakeholder-driven architecture and Entra ID SSO."),
        ]

        component_map: dict[str, ProjectComponent] = {}
        for order, (name, desc) in enumerate(components_data, start=1):
            component = ProjectComponent(
                project_id=project.id,
                name=name,
                description=desc,
                display_order=order,
            )
            session.add(component)
            session.flush()
            component_map[name] = component

        logger.info("Created %d components", len(component_map))

        # =================================================================
        # Tasks
        # =================================================================
        tasks_data = [
            # Development tasks
            {
                "title": "Build EAP staff assignments endpoint",
                "category": "Development",
                "type": "New API Route",
                "component": "API",
                "status": "Complete",
                "priority": TaskPriority.HIGH,
                "description": "Full CRUD for EAP staff assignments including viewer endpoint, filters, swap, drop, and assign operations.",
            },
            {
                "title": "Build WFR pipeline base class",
                "category": "Development",
                "type": "New ETL Pipeline",
                "component": "ETL Pipelines",
                "status": "Complete",
                "priority": TaskPriority.HIGH,
                "description": "Shared base class for all Workforce Report pipelines with scrape, load, cleanse, write, and cleanup steps.",
            },
            {
                "title": "Security employee portal (sec-emp)",
                "category": "Development",
                "type": "New Frontend Feature",
                "component": "Frontend",
                "status": "In Progress",
                "priority": TaskPriority.HIGH,
                "description": "Read-only portal for frontline security employees with minimal layout, post orders, announcements, and micro trainings.",
            },
            {
                "title": "Notification system with inbox and receipts",
                "category": "Development",
                "type": "New API Route",
                "component": "API",
                "status": "Complete",
                "priority": TaskPriority.MEDIUM,
                "description": "Notification authoring, targeting, inbox, read/acknowledge tracking, and CSV receipt export.",
            },
            {
                "title": "Post orders role-based viewer",
                "category": "Development",
                "type": "New Frontend Feature",
                "component": "Frontend",
                "status": "In Progress",
                "priority": TaskPriority.MEDIUM,
                "description": "Role-gated post order viewer where officers see their assigned area and supervisors see all.",
            },
            {
                "title": "Containerize API and ETL runner with Docker",
                "category": "Development",
                "type": "Infrastructure",
                "component": None,
                "status": "Not Started",
                "priority": TaskPriority.MEDIUM,
                "description": "Docker Compose setup to run API and ETL runner in separate containers with a shared database volume.",
            },
            # Communication tasks
            {
                "title": "Request 1Password provisioning from IT",
                "category": "Communication",
                "type": "Access / Provisioning Request",
                "component": None,
                "status": "Blocked",
                "priority": TaskPriority.MEDIUM,
                "description": "Need 1Password vault provisioned for the team to replace plaintext .env credentials.",
            },
            {
                "title": "Request Docker installation for local devices and VMs",
                "category": "Communication",
                "type": "Access / Provisioning Request",
                "component": None,
                "status": "Blocked",
                "priority": TaskPriority.MEDIUM,
                "description": "Docker Desktop needs IT approval and installation on dev machines and the production VM.",
            },
            {
                "title": "Coordinate with InfoSec on SSL certificates",
                "category": "Communication",
                "type": "Cross-Team Request",
                "component": None,
                "status": "In Progress",
                "priority": TaskPriority.LOW,
                "description": "Work with information security to provision SSL certificates for local HTTPS development.",
            },
            {
                "title": "Demo EAP viewer to security leadership",
                "category": "Communication",
                "type": "Stakeholder Update",
                "component": None,
                "status": "Complete",
                "priority": TaskPriority.HIGH,
                "description": "Present the EAP viewer functionality to security directors for feedback before wider rollout.",
            },
            # Documentation tasks
            {
                "title": "ETL Pipelines README",
                "category": "Documentation",
                "type": "README",
                "component": "ETL Pipelines",
                "status": "Complete",
                "priority": TaskPriority.MEDIUM,
                "description": "Comprehensive README covering all three pipeline families (EOD, WFR, EAP), architecture, database tables, and configuration.",
            },
            {
                "title": "SWIKI API README",
                "category": "Documentation",
                "type": "README",
                "component": "API",
                "status": "Complete",
                "priority": TaskPriority.MEDIUM,
                "description": "Full API documentation covering all 11 domain routers, architecture, database, configuration, and development workflow.",
            },
            {
                "title": "Swiki Frontend README",
                "category": "Documentation",
                "type": "README",
                "component": "Frontend",
                "status": "Complete",
                "priority": TaskPriority.MEDIUM,
                "description": "Frontend README covering stakeholder portal architecture, auth flow, routing, theming, and adding new stakeholders.",
            },
            {
                "title": "EAP post assignment playbook",
                "category": "Documentation",
                "type": "Playbook",
                "component": None,
                "status": "Not Started",
                "priority": TaskPriority.LOW,
                "description": "Operational playbook for security managers explaining how to use the EAP viewer to manage staff post assignments.",
            },
            {
                "title": "HSE emergency preparedness program document",
                "category": "Documentation",
                "type": "Program Document",
                "component": "Frontend",
                "status": "In Review",
                "priority": TaskPriority.MEDIUM,
                "description": "Digital version of the HSE emergency preparedness program for the HSE portal.",
            },
        ]

        for task_data in tasks_data:
            category = category_map[task_data["category"]]
            task_type = type_map.get(task_data["type"])
            status_def = status_map[task_data["status"]]
            component = component_map.get(task_data["component"]) if task_data["component"] else None

            task = Task(
                project_id=project.id,
                category_id=category.id,
                type_id=task_type.id if task_type else None,
                status_id=status_def.id,
                component_id=component.id if component else None,
                title=task_data["title"],
                description=task_data.get("description"),
                priority=task_data.get("priority", TaskPriority.MEDIUM),
                completed_at=None,  # Could backfill for Complete tasks if desired
            )
            session.add(task)

        session.commit()

        logger.info("Created %d tasks", len(tasks_data))
        logger.info("Seed complete.")


if __name__ == "__main__":
    seed()