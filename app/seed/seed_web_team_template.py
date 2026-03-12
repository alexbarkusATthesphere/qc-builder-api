"""Seed the database with the Web Development template and the mySphere project.

Usage:
    1. Start the API once so init_db() creates all tables.
    2. Run this script:

        python -m app.seed.seed_web_team_template

    The script is idempotent-ish: it checks for the template by name
    before inserting. If "Web Development" already exists, it skips.

Changes (v2 — commit-aligned dates + environment tracking):
    - start_date and completed_at now reflect actual git commit history
    - environment field tags each task as DEV, TEST, or PROD
"""

import logging
import sys
from datetime import date, datetime
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
from app.models.db.task import TaskEnvironment, TaskPriority

logger = logging.getLogger(__name__)

# Shorthand aliases
HIGH = TaskPriority.HIGH
MED = TaskPriority.MEDIUM
LOW = TaskPriority.LOW
CRIT = TaskPriority.CRITICAL

DEV = TaskEnvironment.DEV
TEST = TaskEnvironment.TEST
PROD = TaskEnvironment.PROD


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _d(date_str: str | None) -> date | None:
    """Parse 'YYYY-MM-DD' into a date, or return None."""
    if date_str is None:
        return None
    return date.fromisoformat(date_str)


def _dt(date_str: str | None) -> datetime | None:
    """Parse 'YYYY-MM-DD' into a midnight datetime, or return None."""
    if date_str is None:
        return None
    return datetime.fromisoformat(date_str)


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
        session.flush()

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
                    ("Cross-Team Request",            "Request or coordinate work with another team."),
                    ("Stakeholder Update",            "Provide a status update or demo to stakeholders."),
                    ("Access / Provisioning Request", "Request access, credentials, licenses, or infrastructure."),
                    ("Vendor Coordination",           "Coordinate with an external vendor or contractor."),
                ],
            },
            "Documentation": {
                "description": "Technical documentation, playbooks, READMEs, and reference material.",
                "display_order": 3,
                "icon": "file-text",
                "color": "#10B981",
                "types": [
                    ("README",           "Repository or project README file."),
                    ("Technical Doc",    "Architecture docs, design docs, or technical specifications."),
                    ("Playbook",         "Operational playbook or runbook for a process."),
                    ("Program Document", "HSE program, policy, or compliance document."),
                    ("Runbook",          "Step-by-step operational procedure for incident response or maintenance."),
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
        # Project: mySphere
        # =================================================================
        project = Project(
            template_id=template.id,
            name="mySphere",
            description=(
                "Multi-stakeholder internal knowledge base and operations portal for The Sphere. "
                "Includes ETL pipelines for data ingestion, a FastAPI backend (swiki-api), and an "
                "Angular frontend (swiki) with role-gated portals for executives, security, HSE, "
                "and developers. Dev environment is feature-complete with fake data. Currently "
                "standing up the VM environment and working through infrastructure blockers before "
                "moving to test with real data."
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
            ("API",           "FastAPI REST backend serving 11 domain routers for the mySphere portal."),
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
        #
        # Organized by category, then by component. Each task uses:
        #   cat   = category name (key into category_map)
        #   typ   = type name (key into type_map)
        #   comp  = component name (key into component_map) or None
        #   st    = status name (key into status_map)
        #   pri   = priority enum
        #   env   = environment enum (DEV, TEST, or PROD)
        #   start = start_date — first related git commit (YYYY-MM-DD)
        #   end   = completed_at — last related git commit (YYYY-MM-DD)
        # =================================================================

        tasks_data = [
            # -----------------------------------------------------------------
            # DEVELOPMENT -- ETL Pipelines
            # -----------------------------------------------------------------
            {
                "title": "EOD employee data pipeline (roster + PTO loader)",
                "cat": "Development", "typ": "New ETL Pipeline", "comp": "ETL Pipelines", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-01-19", "end": "2026-01-19",
                "description": "Loads employee roster and PTO schedule from CSV/Excel. Writes employee_details and pto_data tables.",
            },
            {
                "title": "EOD event data pipeline (TeamUp ICS feed)",
                "cat": "Development", "typ": "New ETL Pipeline", "comp": "ETL Pipelines", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-01-19", "end": "2026-01-19",
                "description": "Parses the TeamUp ICS calendar feed into canonical event records. Writes sphere_events table.",
            },
            {
                "title": "EOD draft calendar with fairness-based scheduling",
                "cat": "Development", "typ": "New ETL Pipeline", "comp": "ETL Pipelines", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-01-19", "end": "2026-01-19",
                "description": "Joins employees, PTO, and events. Applies role eligibility, PTO constraints, and fairness rules to produce eod_calendar_entries.",
            },
            {
                "title": "WFR pipeline base class (shared scrape/load/cleanse/write steps)",
                "cat": "Development", "typ": "Refactor", "comp": "ETL Pipelines", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-02-24", "end": "2026-02-25",
                "description": "Shared base class for all Workforce Report pipelines with configurable 6-step execution: scrape, load, cleanse, write, cleanup, log.",
            },
            {
                "title": "WFR assignments by station pipeline",
                "cat": "Development", "typ": "New ETL Pipeline", "comp": "ETL Pipelines", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-02-25", "end": "2026-02-26",
                "description": "Staff schedule assignments from Workforce. Date-based upsert on schedule_date.",
            },
            {
                "title": "WFR employee contact information pipeline",
                "cat": "Development", "typ": "New ETL Pipeline", "comp": "ETL Pipelines", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-02-25", "end": "2026-02-26",
                "description": "Employee contact details from Workforce. Full-replace snapshot table.",
            },
            {
                "title": "WFR qualifications pipeline",
                "cat": "Development", "typ": "New ETL Pipeline", "comp": "ETL Pipelines", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-02-25", "end": "2026-02-26",
                "description": "Employee qualifications and certifications from Workforce. Full-replace snapshot table.",
            },
            {
                "title": "WFR timesheet detail query pipeline",
                "cat": "Development", "typ": "New ETL Pipeline", "comp": "ETL Pipelines", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-02-25", "end": "2026-02-26",
                "description": "Timesheet line items from Workforce. Date-based upsert on tsd_date.",
            },
            {
                "title": "Composable Workforce Selenium scraper",
                "cat": "Development", "typ": "Infrastructure", "comp": "ETL Pipelines", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-02-13", "end": "2026-02-25",
                "description": "Single-report Workforce scraper (run_wfr.py) that logs in, navigates to a saved Favorites report, selects all parameters, exports CSV, and moves to Exports folder.",
            },
            {
                "title": "EAP reference tables loader",
                "cat": "Development", "typ": "New ETL Pipeline", "comp": "ETL Pipelines", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-01-22", "end": "2026-01-27",
                "description": "Loads 7 EAP reference tables (briefings, venues, levels, sub-levels, posts, post_by_event_type, venue_post_groups) from Excel into SQL.",
            },
            {
                "title": "EAP fresh data generation pipeline",
                "cat": "Development", "typ": "New ETL Pipeline", "comp": "ETL Pipelines", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-01-22", "end": "2026-02-13",
                "description": "Scrapes Workforce and Tableau, loads references from SQL, runs EAP generator logic (shifts, posts, groups, briefings), writes eap_staff_assignments and eap_ungrouped_shifts.",
            },
            {
                "title": "EAP historical data batch loader",
                "cat": "Development", "typ": "New ETL Pipeline", "comp": "ETL Pipelines", "st": "Complete", "pri": LOW,
                "env": DEV, "start": "2026-01-27", "end": "2026-02-25",
                "description": "Batch-loads historical EAP Excel/CSV files (EAP_MONTH_DAY_YEAR.xlsx naming convention) into eap_staff_assignments and eap_ungrouped_shifts tables.",
            },
            {
                "title": "Shared data loaders (file, API, SQL)",
                "cat": "Development", "typ": "Infrastructure", "comp": "ETL Pipelines", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-01-19", "end": "2026-01-19",
                "description": "Three reusable loaders: load_file_data.py (CSV/Excel/TXT), load_api_data.py (TeamUp ICS feed), load_sql_data.py (SQLite reader with dataclass conversion).",
            },
            {
                "title": "SQLite writer with ETL logging and write strategies",
                "cat": "Development", "typ": "Infrastructure", "comp": "ETL Pipelines", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-01-19", "end": "2026-02-25",
                "description": "SQLiteWriter supporting date-based upsert and full-replace strategies. Automatically writes etl_log entries on every operation including failures.",
            },
            {
                "title": "Data validators and schema validation",
                "cat": "Development", "typ": "Infrastructure", "comp": "ETL Pipelines", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-01-19", "end": "2026-02-13",
                "description": "Validation utilities in validators/: cleanse_file_data.py for file-based cleansing, validate_against_model.py for schema validation against frozen dataclasses.",
            },
            {
                "title": "ETL config system (.env based)",
                "cat": "Development", "typ": "Infrastructure", "comp": "ETL Pipelines", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-01-19", "end": "2026-01-19",
                "description": "Central config.py that loads all pipeline configuration from a .env file. Variables grouped by pipeline family (EOD, WFR, EAP) with sensible defaults.",
            },
            {
                "title": "Refactor EAP pipeline to pull from WFR tables instead of legacy scraper",
                "cat": "Development", "typ": "Refactor", "comp": "ETL Pipelines", "st": "Not Started", "pri": LOW,
                "env": DEV, "start": None, "end": None,
                "description": "Replace eap_data_scraper.py (legacy monolithic Selenium scraper) with direct reads from WFR pipeline tables. Generate EAP via SQL instead of re-scraping Workforce.",
            },
            {
                "title": "Production database writer (MySQL/SQL Server)",
                "cat": "Development", "typ": "Infrastructure", "comp": "ETL Pipelines", "st": "Blocked", "pri": HIGH,
                "env": DEV, "start": "2026-02-26", "end": None,
                "description": "write_to_sql_db.py for production. Same interface as SQLite writer but targeting the production database. Blocked on database provisioning and write permissions.",
            },

            # -----------------------------------------------------------------
            # DEVELOPMENT -- API
            # -----------------------------------------------------------------
            {
                "title": "Employees router (directory, org layout, leadership hierarchy)",
                "cat": "Development", "typ": "New API Route", "comp": "API", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-01-19", "end": "2026-01-19",
                "description": "5 endpoints: list with filters, get by name, org-layout (hierarchical by location/department), leadership-roles, and org-hierarchy with reporting chains.",
            },
            {
                "title": "PTO router (CRUD + bulk operations + move)",
                "cat": "Development", "typ": "New API Route", "comp": "API", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-01-19", "end": "2026-01-21",
                "description": "7 endpoints: list, get by employee, create, delete, bulk-create, bulk-delete, and atomic move to new date.",
            },
            {
                "title": "Calendars router (EOD calendar, sphere events, executive unavailability)",
                "cat": "Development", "typ": "New API Route", "comp": "API", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-01-19", "end": "2026-01-21",
                "description": "10 endpoints spanning EOD CRUD (by day, by month, reassign), sphere events (by range, by day), and executive unavailability (PTO joined with employee details).",
            },
            {
                "title": "EAP router (viewer, staff assignments, breaks, swap, changelog)",
                "cat": "Development", "typ": "New API Route", "comp": "API", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-02-03", "end": "2026-02-27",
                "description": "17+ endpoints. Combined viewer page load, staff CRUD with assign/drop/swap, break records, filter options, stats, ungrouped shifts, changelog audit log, and reference edit options.",
            },
            {
                "title": "Post Orders router (packages, areas, items, role-based viewer)",
                "cat": "Development", "typ": "New API Route", "comp": "API", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-02-04", "end": "2026-02-09",
                "description": "Full CRUD for versioned packages, areas, and items. Role-based viewer endpoint where officers see their assigned area and supervisors see all. System-wide overview stats.",
            },
            {
                "title": "Notifications router (inbox, authoring, targeting, receipts, CSV export)",
                "cat": "Development", "typ": "New API Route", "comp": "API", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-02-05", "end": "2026-03-10",
                "description": "10 endpoints: inbox with counts, read/acknowledge/mark-all-read, sent with receipt reports, CSV receipt export, recipient preview, and notification creation.",
            },
            {
                "title": "Announcements router (category-scoped with soft delete and restore)",
                "cat": "Development", "typ": "New API Route", "comp": "API", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-02-05", "end": "2026-02-05",
                "description": "7 endpoints: list visible to current user, counts, get by ID, create (Mgr+ required), update (author or EXEC/DEV), soft-delete, and restore.",
            },
            {
                "title": "Wiki Users router (authentication, RBAC, activate/deactivate)",
                "cat": "Development", "typ": "New API Route", "comp": "API", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-02-05", "end": "2026-02-09",
                "description": "12 endpoints: list with filters, privileged/dev users, lookup by email, authenticate, notification targets by category, CRUD, soft deactivate/activate, hard delete.",
            },
            {
                "title": "Ticketing Forms router (dynamic form builder with labels, questions, options)",
                "cat": "Development", "typ": "New API Route", "comp": "API", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-03-05", "end": "2026-03-05",
                "description": "4 CRUD groups: section header labels, reusable field definitions, option groups and values, and named form definitions with slug-based resolution and question reordering.",
            },
            {
                "title": "Reference Tables router (venue/post hierarchy CRUD)",
                "cat": "Development", "typ": "New API Route", "comp": "API", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-03-05", "end": "2026-03-05",
                "description": "Full CRUD for the venue/event/post hierarchy used by EAP generation and the dev portal. Covers venues, levels, sub-levels, posts, briefings, and lookup helpers.",
            },
            {
                "title": "ETL Controller router (process registry, subprocess runner, log viewer)",
                "cat": "Development", "typ": "New API Route", "comp": "API", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-02-26", "end": "2026-02-26",
                "description": "7 endpoints: list processes, health summary, paginated logs, run history, active jobs, trigger run, and re-run failed. Subprocess executor with concurrency guard.",
            },
            {
                "title": "API layered architecture (FastAPI, SQLModel, Pydantic, Alembic)",
                "cat": "Development", "typ": "Infrastructure", "comp": "API", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-01-16", "end": "2026-01-19",
                "description": "5-layer architecture: routers, Pydantic schemas, repositories, SQLModel ORM, and database. Alembic configured for migrations. CORS, SSL support, lifespan events.",
            },
            {
                "title": "Dockerfile and docker-compose configuration",
                "cat": "Development", "typ": "Infrastructure", "comp": "API", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-03-06", "end": "2026-03-06",
                "description": "Dockerfile for the API and parent-level docker-compose.yaml to orchestrate API and ETL runner in separate containers with a shared database volume. Files are in place.",
            },
            {
                "title": "Connect API to production database (replace SQLite connection)",
                "cat": "Development", "typ": "Infrastructure", "comp": "API", "st": "Blocked", "pri": HIGH,
                "env": TEST, "start": None, "end": None,
                "description": "Swap DATABASE_URL from SQLite to production connection string. Blocked on database provisioning, schema creation, and write permissions.",
            },
            {
                "title": "ETL runner working on the VM (currently local only)",
                "cat": "Development", "typ": "Infrastructure", "comp": "API", "st": "Blocked", "pri": HIGH,
                "env": DEV, "start": None, "end": None,
                "description": "The ETL controller subprocess runner works locally but has environment issues on the VM. Expect Docker containerization to resolve this.",
            },

            # -----------------------------------------------------------------
            # DEVELOPMENT -- Frontend
            # -----------------------------------------------------------------
            {
                "title": "Shell layout with dynamic stakeholder theming",
                "cat": "Development", "typ": "New Frontend Feature", "comp": "Frontend", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-01-15", "end": "2026-01-20",
                "description": "Shared ShellComponent wrapping all protected routes. Applies CSS custom properties scoped to the active stakeholder's theme class (theme-executives, theme-sec, etc.).",
            },
            {
                "title": "Two-pass authentication (MSAL + backend role verification)",
                "cat": "Development", "typ": "New Frontend Feature", "comp": "Frontend", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-01-22", "end": "2026-01-28",
                "description": "Pass 1 validates email domain via Entra ID. Pass 2 verifies roles against backend API. Full mock auth system for local development without Azure credentials.",
            },
            {
                "title": "Route guards (auth, role, category, public-only, unauthorized)",
                "cat": "Development", "typ": "New Frontend Feature", "comp": "Frontend", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-01-22", "end": "2026-02-05",
                "description": "5 guards: authGuard (full session), publicOnlyGuard (login page), roleGuard factory, categoryGuard factory with traversal, and unauthorizedGuard.",
            },
            {
                "title": "Stakeholder config system (declarative registry)",
                "cat": "Development", "typ": "New Frontend Feature", "comp": "Frontend", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-01-15", "end": "2026-02-11",
                "description": "Central stakeholder.config.ts registry. Each portal defined declaratively with navigation, theming, required roles, and layout options. Source of truth for the entire app.",
            },
            {
                "title": "SSO landing page, auth callback, and unauthorized page",
                "cat": "Development", "typ": "New Frontend Feature", "comp": "Frontend", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-01-22", "end": "2026-01-28",
                "description": "Login page with Entra ID SSO trigger, MSAL redirect handler for auth-callback, and access denied page with unauthorized guard.",
            },
            {
                "title": "Executive portal (dashboard, org profile, calendar, resources, finance)",
                "cat": "Development", "typ": "New Frontend Feature", "comp": "Frontend", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-01-20", "end": "2026-03-05",
                "description": "8 routes: landing, operations dashboard, org profile, playbooks/resources, finance report, calendar deep-link, sphere events calendar, and executive unavailability.",
            },
            {
                "title": "Security manager portal (workforce, EAP viewer, notifications, reports, resources)",
                "cat": "Development", "typ": "New Frontend Feature", "comp": "Frontend", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-01-26", "end": "2026-03-10",
                "description": "13 routes: landing, operations dashboard, notifications, EAP viewer, reporting, flash report, resources hub, emergency procedures, micro trainings, radio/wand inventory, emergency contacts, radio channels.",
            },
            {
                "title": "Security employee portal (minimal layout, post orders, announcements, trainings)",
                "cat": "Development", "typ": "New Frontend Feature", "comp": "Frontend", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-02-03", "end": "2026-02-09",
                "description": "9 routes with minimalLayout (no sidebar). Landing/dashboard, my post orders, sphere events, announcements, micro trainings hub with individual training pages, and resources.",
            },
            {
                "title": "HSE portal (programs, SOPs, forms, calendars, resources)",
                "cat": "Development", "typ": "New Frontend Feature", "comp": "Frontend", "st": "Complete", "pri": HIGH,
                "env": DEV, "start": "2026-01-23", "end": "2026-02-27",
                "description": "14 routes: landing, 7 program pages (HIPP, BIPP, EP, eyewash, LOTO, PPE, SCM), events calendar, walkthrough calendar, SOPs, resources, property inspection checklist, incident response form.",
            },
            {
                "title": "Developer portal (ETL dashboard, tickets, form manager, reference tables)",
                "cat": "Development", "typ": "New Frontend Feature", "comp": "Frontend", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-02-26", "end": "2026-03-05",
                "description": "8 routes: landing/overview, ETL pipeline dashboard, ticket table, form manager (list/new/edit/preview), and reference table editor.",
            },
            {
                "title": "Mock data system for offline development",
                "cat": "Development", "typ": "Infrastructure", "comp": "Frontend", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-01-15", "end": "2026-01-20",
                "description": "environment.ts useMockData flag for CSV-based offline development. Allows frontend work without a running backend.",
            },
            {
                "title": "Mock authentication for local dev without Azure credentials",
                "cat": "Development", "typ": "Infrastructure", "comp": "Frontend", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-01-22", "end": "2026-01-28",
                "description": "useMockAuth flag bypasses Entra ID entirely. mockUserRoles array allows testing different portal access levels locally.",
            },

            # -----------------------------------------------------------------
            # DEVELOPMENT -- Cross-Component / Infrastructure
            # -----------------------------------------------------------------
            {
                "title": "Stand up dev environment on the VM",
                "cat": "Development", "typ": "Infrastructure", "comp": None, "st": "In Progress", "pri": CRIT,
                "env": DEV, "start": "2026-02-27", "end": None,
                "description": "Get the full dev environment (API, ETL runner, frontend) running on the VM. Currently being manually stood up while waiting on Docker and TLS.",
            },
            {
                "title": "Configure self-signed TLS certificates on the VM",
                "cat": "Development", "typ": "Infrastructure", "comp": None, "st": "In Progress", "pri": HIGH,
                "env": DEV, "start": "2026-02-27", "end": None,
                "description": "Set up self-signed certs for HTTPS on the VM as an interim solution. Requires manual configuration each time while waiting on proper cert provisioning.",
            },
            {
                "title": "Containerize services with Docker on the VM",
                "cat": "Development", "typ": "Infrastructure", "comp": None, "st": "Blocked", "pri": HIGH,
                "env": DEV, "start": None, "end": None,
                "description": "Run API and ETL runner in Docker containers on the VM using the existing docker-compose.yaml. Blocked on Docker/virtualization approval for the VM.",
            },
            {
                "title": "Connect to production database (schemas, tables, write permissions)",
                "cat": "Development", "typ": "Infrastructure", "comp": None, "st": "Blocked", "pri": HIGH,
                "env": TEST, "start": None, "end": None,
                "description": "Create database schemas and tables on the production database server. Blocked on DBA provisioning and write permission grants.",
            },
            {
                "title": "InfoSec security scan of VM (with fake data)",
                "cat": "Development", "typ": "Infrastructure", "comp": None, "st": "Not Started", "pri": HIGH,
                "env": DEV, "start": None, "end": None,
                "description": "Have InfoSec scan the VM while it is still running with fake data only. Must happen before any real data touches the environment.",
            },
            {
                "title": "Address InfoSec action items from scan",
                "cat": "Development", "typ": "Infrastructure", "comp": None, "st": "Not Started", "pri": HIGH,
                "env": DEV, "start": None, "end": None,
                "description": "Remediate any findings from the InfoSec scan. This is a prerequisite for moving to the test environment with real data.",
            },
            {
                "title": "Stand up test environment with real data",
                "cat": "Development", "typ": "Infrastructure", "comp": None, "st": "Not Started", "pri": HIGH,
                "env": TEST, "start": None, "end": None,
                "description": "Once the dev environment is fully working on the VM with Docker, database connectivity, and InfoSec clearance, stand up a test environment connected to real data sources.",
            },

            # -----------------------------------------------------------------
            # COMMUNICATION
            # -----------------------------------------------------------------
            {
                "title": "Request 1Password provisioning from IT",
                "cat": "Communication", "typ": "Access / Provisioning Request", "comp": None, "st": "Blocked", "pri": MED,
                "env": DEV, "start": None, "end": None,
                "description": "Need 1Password vault provisioned for the team to replace plaintext .env credentials. Will support both CLI (op run) and SDK-based approaches.",
            },
            {
                "title": "Request Docker/virtualization approval for VM",
                "cat": "Communication", "typ": "Access / Provisioning Request", "comp": None, "st": "Blocked", "pri": HIGH,
                "env": DEV, "start": None, "end": None,
                "description": "Docker needs IT approval and installation on the VM. Required for containerizing the API and ETL runner.",
            },
            {
                "title": "Request database write permissions and schema creation",
                "cat": "Communication", "typ": "Access / Provisioning Request", "comp": None, "st": "Blocked", "pri": HIGH,
                "env": TEST, "start": None, "end": None,
                "description": "Request DBA team to create the production database schemas and tables, and grant write permissions to the application service account.",
            },
            {
                "title": "Coordinate with InfoSec for VM security scan",
                "cat": "Communication", "typ": "Cross-Team Request", "comp": None, "st": "Not Started", "pri": HIGH,
                "env": DEV, "start": None, "end": None,
                "description": "Schedule the InfoSec security scan of the VM. Must be done while only fake data is present, before connecting to real data sources.",
            },
            {
                "title": "Coordinate TLS certificate process (self-signed interim, real certs later)",
                "cat": "Communication", "typ": "Cross-Team Request", "comp": None, "st": "In Progress", "pri": MED,
                "env": DEV, "start": "2026-02-27", "end": None,
                "description": "Working with InfoSec on the TLS certificate process. Using self-signed certs as an interim solution on the VM while proper certs are being provisioned.",
            },
            {
                "title": "Coordinate with InfoSec on scan action items before test environment",
                "cat": "Communication", "typ": "Cross-Team Request", "comp": None, "st": "Not Started", "pri": HIGH,
                "env": TEST, "start": None, "end": None,
                "description": "After the scan, coordinate with InfoSec to understand and prioritize the remediation items. Must be resolved before real data enters the environment.",
            },

            # -----------------------------------------------------------------
            # DOCUMENTATION
            # -----------------------------------------------------------------
            {
                "title": "ETL Pipelines README",
                "cat": "Documentation", "typ": "README", "comp": "ETL Pipelines", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-01-19", "end": "2026-03-11",
                "description": "Comprehensive README covering all three pipeline families (EOD, WFR, EAP), architecture, repository structure, database tables, write strategies, configuration, testing, and troubleshooting.",
            },
            {
                "title": "SWIKI API README",
                "cat": "Documentation", "typ": "README", "comp": "API", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-01-19", "end": "2026-03-11",
                "description": "Full API documentation covering all 11 domain routers with endpoint tables, layered architecture, project structure, database, configuration, Docker plans, and development workflow.",
            },
            {
                "title": "Swiki Frontend README",
                "cat": "Documentation", "typ": "README", "comp": "Frontend", "st": "Complete", "pri": MED,
                "env": DEV, "start": "2026-03-11", "end": "2026-03-11",
                "description": "Frontend README covering stakeholder portal architecture, 5 portal route references, two-pass authentication, route guards, project structure, environment config, and adding new stakeholders.",
            },
            {
                "title": "QC Builder API README",
                "cat": "Documentation", "typ": "README", "comp": None, "st": "Complete", "pri": MED,
                "env": DEV, "start": None, "end": None,
                "description": "README for the QC Builder API covering data model hierarchy, API surface, architecture, database schema, configuration, and design decisions.",
            },
        ]

        # Insert all tasks
        for task_data in tasks_data:
            category = category_map[task_data["cat"]]
            task_type = type_map.get(task_data["typ"])
            status_def = status_map[task_data["st"]]
            component = component_map.get(task_data["comp"]) if task_data.get("comp") else None

            task = Task(
                project_id=project.id,
                category_id=category.id,
                type_id=task_type.id if task_type else None,
                status_id=status_def.id,
                component_id=component.id if component else None,
                title=task_data["title"],
                description=task_data.get("description"),
                priority=task_data.get("pri", MED),
                environment=task_data.get("env"),
                start_date=_d(task_data.get("start")),
                completed_at=_dt(task_data.get("end")),
            )
            session.add(task)

        session.commit()

        logger.info("Created %d tasks", len(tasks_data))
        logger.info("Seed complete.")


if __name__ == "__main__":
    seed()