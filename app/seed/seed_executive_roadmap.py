"""
Seed the executive roadmap with the updated 5-phase structure.

Location: app/seed/seed_executive_roadmap.py

Replaces all template-2 categories, types, and project-2 tasks with
the restructured data aligned to the mySphere roadmap document (V2.0).

Phase mapping to roadmap sections:
    1. Development           → A. Proof of Concept + B. Project Architecture
    2. Implementation        → C. Infra, Security & Prod Readiness (absorbs old Expansion)
    3. Core Rollout          → D. Developer Testing + E. Beta Release + F. Production Release
    4. Enhancements & Opt.   → Current hardening, testing, docs, ops readiness
    5. Expansion             → G–I (Scalability/R&D) + J–L (Integrations/Features/Analytics)

Template 1 (Web Development) and project 1 tasks are NOT touched.

Date strategy:
    - Development:    Dates derived from git commit history across three repos
    - Implementation: Anchored to current blocker state + realistic provisioning lead times
    - Core Rollout:   Follows test environment availability → beta → go-live
    - Enhancements:   Parallels late Implementation and Core Rollout
    - Expansion:      Post-launch (Jan–Apr 2027)

Usage:
    python -m app.seed.seed_executive_roadmap
"""

import logging
import sys
from datetime import date, datetime
from pathlib import Path

from sqlmodel import Session, select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.core.database import engine, init_db
from app.core.logging import setup_logging
from app.models.db import (  # noqa: F401
    Project, ProjectComponent, StatusDefinition, Task, TaskCategory, TaskType, Template,
)
from app.models.db.task import TaskComment, TaskEnvironment, TaskHistory, TaskPriority

logger = logging.getLogger(__name__)

HIGH = TaskPriority.HIGH
MED = TaskPriority.MEDIUM
LOW = TaskPriority.LOW
CRIT = TaskPriority.CRITICAL
DEV = TaskEnvironment.DEV
TEST = TaskEnvironment.TEST
PROD = TaskEnvironment.PROD

TEMPLATE_NAME = "Executive Roadmap Summary"
PROJECT_NAME = "mySphere Executive Roadmap"


def _d(s: str | None) -> date | None:
    return date.fromisoformat(s) if s else None

def _dt(s: str | None) -> datetime | None:
    return datetime.fromisoformat(s) if s else None


def seed() -> None:
    setup_logging()
    init_db()

    with Session(engine) as session:
        template = session.exec(select(Template).where(Template.name == TEMPLATE_NAME)).first()
        if not template:
            logger.error("Template '%s' not found. Run the initial seed first.", TEMPLATE_NAME)
            return
        project = session.exec(select(Project).where(Project.name == PROJECT_NAME)).first()
        if not project:
            logger.error("Project '%s' not found.", PROJECT_NAME)
            return

        logger.info("Found template id=%s and project id=%s", template.id, project.id)

        # --- Clear existing tasks, comments, history ---
        project_tasks = list(session.exec(select(Task).where(Task.project_id == project.id)).all())
        for t in project_tasks:
            for c in session.exec(select(TaskComment).where(TaskComment.task_id == t.id)).all():
                session.delete(c)
            for h in session.exec(select(TaskHistory).where(TaskHistory.task_id == t.id)).all():
                session.delete(h)
            session.delete(t)
        session.flush()
        logger.info("Cleared %d existing tasks", len(project_tasks))

        # --- Clear old categories and types ---
        old_cats = list(session.exec(select(TaskCategory).where(TaskCategory.template_id == template.id)).all())
        for cat in old_cats:
            for typ in session.exec(select(TaskType).where(TaskType.category_id == cat.id)).all():
                session.delete(typ)
            session.delete(cat)
        session.flush()
        logger.info("Cleared %d old categories", len(old_cats))

        # --- Reference maps ---
        status_map = {s.name: s for s in session.exec(select(StatusDefinition).where(StatusDefinition.template_id == template.id)).all()}
        component_map = {c.name: c for c in session.exec(select(ProjectComponent).where(ProjectComponent.project_id == project.id)).all()}

        # --- Create 5 phases ---
        # fmt: off
        categories_config = {
            "Development": {
                "description": "Core application build: ETL pipeline families, API domain routers, frontend stakeholder portals, and foundational infrastructure.",
                "display_order": 1, "icon": "code", "color": "#3B82F6",
                "types": [
                    ("Pipeline Family",       "A complete ETL pipeline family (multiple related pipelines)."),
                    ("API Domain",            "One or more related API routers serving a functional domain."),
                    ("Frontend Portal",       "A stakeholder portal with its full route tree."),
                    ("Frontend Foundation",   "Cross-cutting frontend infrastructure (auth, theming, shell)."),
                    ("Shared Infrastructure", "Reusable utilities, base classes, config, and tooling."),
                ],
            },
            "Implementation": {
                "description": "Environment standup, provisioning, security clearance, repository scaffolding, environment translation, and cross-team coordination to get services running in DEV, TEST, and PROD.",
                "display_order": 2, "icon": "server", "color": "#8B5CF6",
                "types": [
                    ("Environment Standup",     "Standing up a full environment (VM, Docker, networking, TLS)."),
                    ("Provisioning Request",    "Cross-team requests for database, VM, TLS, or credential provisioning."),
                    ("Security Clearance",      "InfoSec scans, remediation, and due diligence for an environment."),
                    ("Service Connectivity",    "Connecting services to databases and infrastructure."),
                    ("Repository Setup",        "Scaffolding a new environment repo with architecture and base config."),
                    ("Environment Translation", "Porting an application layer from one environment to another."),
                ],
            },
            "Core Rollout": {
                "description": "Field testing at live events, controlled beta release with SOPs and training, and production go-live with stability validation.",
                "display_order": 3, "icon": "rocket", "color": "#F59E0B",
                "types": [
                    ("Field Testing",      "Testing application functionality at live events with real-world conditions."),
                    ("Beta Deployment",    "Controlled release to a limited user group with monitoring and feedback."),
                    ("Production Release", "Final production deployment, stability validation, and go-live."),
                    ("SOPs & Training",    "Standard operating procedures, training materials, and instructional content."),
                    ("Support Setup",      "Ticketing systems, helpdesk coordination, and user support infrastructure."),
                ],
            },
            "Enhancements & Optimizations": {
                "description": "Hardening, performance testing, security testing, operational documentation, monitoring, and production readiness activities.",
                "display_order": 4, "icon": "shield", "color": "#10B981",
                "types": [
                    ("Documentation",        "READMEs, technical docs, runbooks, playbooks, and operational guides."),
                    ("Performance Testing",  "Load testing strategy, tooling, execution, and remediation."),
                    ("Security Testing",     "SAST, DAST, pen testing, SCA, auth reviews, and API assessments."),
                    ("Production Hardening", "Secrets management, WAF, CSP, backups, CI/CD, monitoring, logging."),
                    ("Operational Readiness", "SLIs/SLOs, capacity planning, stakeholder demos, training, go-live."),
                ],
            },
            "Expansion": {
                "description": "Post-launch growth: new system integrations, feature expansions, executive analytics, cross-department adoption, scalability assessment, and the repeatable R&D lifecycle.",
                "display_order": 5, "icon": "trending-up", "color": "#EC4899",
                "types": [
                    ("System Integration",        "Connecting new external data sources and third-party systems."),
                    ("Feature Expansion",          "New micro-services and feature modules beyond the core application."),
                    ("Executive Analytics",        "Decision-making tools, venue-wide reporting, and KPI tracking."),
                    ("Scalability Assessment",     "Performance benchmarking, bottleneck analysis, and capacity planning."),
                    ("Cross-Department Adoption",  "Adapting tools and workflows for adoption by additional departments."),
                    ("R&D Lifecycle",              "Repeatable cycle: identify stakeholders, data sources, develop, test, release."),
                ],
            },
        }
        # fmt: on

        category_map: dict[str, TaskCategory] = {}
        type_map: dict[str, TaskType] = {}

        for cat_name, cat_config in categories_config.items():
            types_data = cat_config.pop("types")
            category = TaskCategory(template_id=template.id, name=cat_name, **cat_config)
            session.add(category)
            session.flush()
            category_map[cat_name] = category
            for order, (tname, tdesc) in enumerate(types_data, start=1):
                tt = TaskType(category_id=category.id, name=tname, description=tdesc, display_order=order)
                session.add(tt)
                session.flush()
                type_map[tname] = tt

        logger.info("Created %d categories with %d types", len(category_map), len(type_map))

        # =================================================================
        # Tasks — 73 total, all with start + due dates
        #
        # Fields: cat, typ, comp, st, pri, env, start, due, end, title, description
        # =================================================================

        # fmt: off
        T = tasks_data = [
            # ── DEVELOPMENT (18) ── Jan 15 → Mar 12 ── from git commit history ──
            {"title":"EOD Pipeline Family (roster, events, draft calendar)","cat":"Development","typ":"Pipeline Family","comp":"ETL Pipelines","st":"Complete","pri":HIGH,"env":DEV,"start":"2026-01-15","due":"2026-02-14","end":"2026-02-14","description":"End-of-day pipeline family handling roster snapshots, event data, and draft calendar generation."},
            {"title":"EAP Pipeline Family (references, generator, historical batch)","cat":"Development","typ":"Pipeline Family","comp":"ETL Pipelines","st":"Complete","pri":HIGH,"env":DEV,"start":"2026-01-19","due":"2026-03-05","end":"2026-03-05","description":"Employee assignment planner pipeline family covering reference data, schedule generation, and historical batch processing."},
            {"title":"WFR Pipeline Family (base class + 4 report pipelines)","cat":"Development","typ":"Pipeline Family","comp":"ETL Pipelines","st":"Complete","pri":HIGH,"env":DEV,"start":"2026-02-05","due":"2026-03-11","end":"2026-03-11","description":"Workforce reporting pipeline family with a shared base class and four specialized report pipelines."},
            {"title":"ETL Shared Infrastructure (loaders, writer, validators, config)","cat":"Development","typ":"Shared Infrastructure","comp":"ETL Pipelines","st":"Complete","pri":MED,"env":DEV,"start":"2026-01-15","due":"2026-02-14","end":"2026-02-14","description":"Reusable ETL components including data loaders, the SQLite writer, validators, and centralized configuration."},
            {"title":"Composable Workforce Selenium Scraper","cat":"Development","typ":"Shared Infrastructure","comp":"ETL Pipelines","st":"Complete","pri":HIGH,"env":DEV,"start":"2026-01-28","due":"2026-03-09","end":"2026-03-09","description":"Configurable Selenium-based scraper for extracting workforce data from authenticated web portals."},
            {"title":"Production Database Writer (MySQL/SQL Server)","cat":"Development","typ":"Shared Infrastructure","comp":"ETL Pipelines","st":"Blocked","pri":HIGH,"env":DEV,"start":"2026-03-01","due":"2026-04-14","end":None,"description":"Database writer module targeting MySQL/SQL Server for production use. Blocked pending database provisioning."},
            {"title":"API Layered Architecture & Docker Configuration","cat":"Development","typ":"API Domain","comp":"API","st":"Complete","pri":HIGH,"env":DEV,"start":"2026-01-28","due":"2026-02-14","end":"2026-02-14","description":"Established the layered FastAPI architecture (routers → services → repositories) with Docker containerization."},
            {"title":"Core API Routers: Employees, PTO, Calendars","cat":"Development","typ":"API Domain","comp":"API","st":"Complete","pri":HIGH,"env":DEV,"start":"2026-01-28","due":"2026-02-14","end":"2026-02-14","description":"Core workforce-facing API routers for employee records, PTO management, and calendar data."},
            {"title":"EAP API Router (viewer, staff, breaks, swap, changelog)","cat":"Development","typ":"API Domain","comp":"API","st":"Complete","pri":HIGH,"env":DEV,"start":"2026-02-14","due":"2026-02-28","end":"2026-02-28","description":"Employee assignment planner API router supporting schedule viewing, staff management, break tracking, shift swaps, and change logging."},
            {"title":"Security API Routers: Post Orders, Notifications, Announcements, Wiki Users","cat":"Development","typ":"API Domain","comp":"API","st":"Complete","pri":HIGH,"env":DEV,"start":"2026-02-14","due":"2026-03-05","end":"2026-03-05","description":"Security-domain API routers for post orders, notification delivery, announcements, and wiki user management."},
            {"title":"Developer API Routers: Ticketing Forms, Reference Tables, ETL Controller","cat":"Development","typ":"API Domain","comp":"API","st":"Complete","pri":MED,"env":DEV,"start":"2026-03-01","due":"2026-03-11","end":"2026-03-11","description":"Developer-facing API routers for ticketing form submissions, reference table lookups, and ETL pipeline control."},
            {"title":"Frontend Foundation: Shell, Theming, Stakeholder Config, Mock Data","cat":"Development","typ":"Frontend Foundation","comp":"Frontend","st":"Complete","pri":HIGH,"env":DEV,"start":"2026-02-01","due":"2026-02-22","end":"2026-02-22","description":"Angular application shell with theming engine, stakeholder-driven configuration system, and mock data layer."},
            {"title":"Authentication & Authorization System","cat":"Development","typ":"Frontend Foundation","comp":"Frontend","st":"Complete","pri":HIGH,"env":DEV,"start":"2026-02-01","due":"2026-02-22","end":"2026-02-22","description":"Two-pass Entra ID authentication with role-based route guards and stakeholder-scoped authorization."},
            {"title":"Executive Portal","cat":"Development","typ":"Frontend Portal","comp":"Frontend","st":"Complete","pri":HIGH,"env":DEV,"start":"2026-02-22","due":"2026-03-05","end":"2026-03-05","description":"Executive stakeholder portal with high-level dashboards, KPI views, and operational summaries."},
            {"title":"Security Manager Portal","cat":"Development","typ":"Frontend Portal","comp":"Frontend","st":"Complete","pri":HIGH,"env":DEV,"start":"2026-02-22","due":"2026-03-05","end":"2026-03-05","description":"Security management portal for post orders, staffing oversight, notifications, and announcements."},
            {"title":"HSE Portal","cat":"Development","typ":"Frontend Portal","comp":"Frontend","st":"Complete","pri":HIGH,"env":DEV,"start":"2026-03-01","due":"2026-03-09","end":"2026-03-09","description":"Health, safety, and environment portal for compliance tracking, incident management, and HSE reporting."},
            {"title":"Security Employee Portal","cat":"Development","typ":"Frontend Portal","comp":"Frontend","st":"Complete","pri":HIGH,"env":DEV,"start":"2026-03-05","due":"2026-03-11","end":"2026-03-11","description":"Frontline security employee portal for viewing assignments, schedules, post orders, and announcements."},
            {"title":"Developer Portal","cat":"Development","typ":"Frontend Portal","comp":"Frontend","st":"Complete","pri":MED,"env":DEV,"start":"2026-03-09","due":"2026-03-12","end":"2026-03-12","description":"Developer-facing portal for ETL monitoring, ticketing forms, reference table management, and system diagnostics."},

            # ── IMPLEMENTATION (18) ── Jan 15 → Sep 28 ──
            {"title":"Dev Environment Standup (VM, Docker, TLS, Networking)","cat":"Implementation","typ":"Environment Standup","comp":None,"st":"Complete","pri":CRIT,"env":DEV,"start":"2026-01-15","due":"2026-03-01","end":"2026-03-01","description":"Full standup of the development environment including VM provisioning, Docker installation, self-signed TLS, and internal networking."},
            {"title":"Test Environment Standup & InfoSec Clearance","cat":"Implementation","typ":"Environment Standup","comp":None,"st":"Not Started","pri":HIGH,"env":TEST,"start":"2026-05-01","due":"2026-05-26","end":None,"description":"Stand up the test environment VM with production-equivalent configuration and obtain InfoSec clearance before introducing real data."},
            {"title":"Production Environment Standup & InfoSec Clearance","cat":"Implementation","typ":"Environment Standup","comp":None,"st":"Not Started","pri":HIGH,"env":PROD,"start":"2026-07-20","due":"2026-08-17","end":None,"description":"Stand up the production environment with hardened OS, production-grade TLS, firewall rules, and full InfoSec clearance."},
            {"title":"ETL Runner Containerization & Verification","cat":"Implementation","typ":"Service Connectivity","comp":"API","st":"In Progress","pri":HIGH,"env":DEV,"start":"2026-03-10","due":"2026-04-07","end":None,"description":"Containerize the ETL runner and verify all pipeline families execute correctly within the Docker environment."},
            {"title":"TLS Certificate Coordination (self-signed → production certs)","cat":"Implementation","typ":"Service Connectivity","comp":None,"st":"In Progress","pri":MED,"env":DEV,"start":"2026-02-27","due":"2026-04-21","end":None,"description":"Transition from self-signed TLS certificates to properly signed production certificates across all services."},
            {"title":"Test Environment Database & API Connectivity","cat":"Implementation","typ":"Service Connectivity","comp":None,"st":"Blocked","pri":HIGH,"env":TEST,"start":"2026-05-26","due":"2026-06-16","end":None,"description":"Connect API and ETL services to the test environment database. Blocked pending database provisioning."},
            {"title":"Production Service & Database Connectivity","cat":"Implementation","typ":"Service Connectivity","comp":None,"st":"Not Started","pri":HIGH,"env":PROD,"start":"2026-09-07","due":"2026-09-28","end":None,"description":"Connect all production services to the production database with validated connection pooling and failover."},
            {"title":"Dev Environment InfoSec Scan & Remediation","cat":"Implementation","typ":"Security Clearance","comp":None,"st":"Not Started","pri":HIGH,"env":DEV,"start":"2026-04-07","due":"2026-04-28","end":None,"description":"InfoSec security scan of the dev environment VM and remediation of all findings before connecting to real data."},
            {"title":"Production InfoSec Coordination & Go-Live Clearance","cat":"Implementation","typ":"Security Clearance","comp":None,"st":"Not Started","pri":HIGH,"env":PROD,"start":"2026-08-17","due":"2026-09-07","end":None,"description":"Full InfoSec coordination for production environment including scan, remediation, and go-live authorization."},
            {"title":"Test Environment Provisioning Requests (DB, VM, TLS, 1Password)","cat":"Implementation","typ":"Provisioning Request","comp":None,"st":"Blocked","pri":HIGH,"env":TEST,"start":"2026-03-18","due":"2026-04-30","end":None,"description":"Cross-team provisioning requests for test environment: database schemas, VM virtualization, TLS certificates, and 1Password vault."},
            {"title":"Production Infrastructure Provisioning (VM, DB, TLS, DNS)","cat":"Implementation","typ":"Provisioning Request","comp":None,"st":"Not Started","pri":HIGH,"env":PROD,"start":"2026-06-22","due":"2026-07-20","end":None,"description":"Cross-team provisioning requests for production: VM compute/storage, database instance, TLS certificates, and DNS configuration."},
            {"title":"Test Environment Repository Scaffolding (Frontend + API)","cat":"Implementation","typ":"Repository Setup","comp":None,"st":"In Progress","pri":MED,"env":TEST,"start":"2026-03-15","due":"2026-04-14","end":None,"description":"Scaffold test environment repositories for the frontend and API with environment-specific configuration, build targets, and deployment scripts."},
            {"title":"Production API Repository Scaffolding","cat":"Implementation","typ":"Repository Setup","comp":"API","st":"Not Started","pri":HIGH,"env":PROD,"start":"2026-07-20","due":"2026-08-10","end":None,"description":"Scaffold the production API repository with hardened configuration, production database connections, and CI/CD integration."},
            {"title":"Production Frontend Repository Scaffolding","cat":"Implementation","typ":"Repository Setup","comp":"Frontend","st":"Not Started","pri":HIGH,"env":PROD,"start":"2026-07-20","due":"2026-08-10","end":None,"description":"Scaffold the production frontend repository with production API endpoints, environment-specific build configuration, and deployment pipeline."},
            {"title":"Port ETL Pipelines to Test Environment","cat":"Implementation","typ":"Environment Translation","comp":"ETL Pipelines","st":"Not Started","pri":HIGH,"env":TEST,"start":"2026-05-01","due":"2026-06-01","end":None,"description":"Translate all ETL pipeline families to the test environment, connecting to provisioned test databases and validating data integrity."},
            {"title":"Port API & Frontend to Test Environment","cat":"Implementation","typ":"Environment Translation","comp":None,"st":"Not Started","pri":HIGH,"env":TEST,"start":"2026-05-26","due":"2026-06-22","end":None,"description":"Translate the FastAPI backend and Angular frontend into the test environment repos with test-specific connection strings and configuration."},
            {"title":"Port ETL Pipelines to Production","cat":"Implementation","typ":"Environment Translation","comp":"ETL Pipelines","st":"Not Started","pri":HIGH,"env":PROD,"start":"2026-08-10","due":"2026-09-07","end":None,"description":"Port all ETL pipeline families to production, replacing SQLite writers with the production database writer and validating against test outputs."},
            {"title":"Refactor EAP Pipeline to Consume WFR Tables","cat":"Implementation","typ":"Environment Translation","comp":"ETL Pipelines","st":"Not Started","pri":LOW,"env":DEV,"start":"2026-06-01","due":"2026-06-29","end":None,"description":"Refactor the EAP pipeline family to consume data from WFR tables instead of independent extraction, reducing duplication and improving data consistency."},

            # ── CORE ROLLOUT (14) ── Jun 22 → Dec 22 ──
            {"title":"Conduct Field Testing at Live Events","cat":"Core Rollout","typ":"Field Testing","comp":None,"st":"Not Started","pri":HIGH,"env":TEST,"start":"2026-06-22","due":"2026-07-20","end":None,"description":"Deploy the application to the test environment and conduct hands-on testing during live events to validate real-world functionality."},
            {"title":"Validate Application UI & Logic in Real-World Conditions","cat":"Core Rollout","typ":"Field Testing","comp":"Frontend","st":"Not Started","pri":HIGH,"env":TEST,"start":"2026-06-22","due":"2026-07-20","end":None,"description":"Verify that all portal views, data displays, and interactive features perform correctly under live event conditions with real data loads."},
            {"title":"Document Test Observations & Improvement Opportunities","cat":"Core Rollout","typ":"Field Testing","comp":None,"st":"Not Started","pri":MED,"env":TEST,"start":"2026-07-06","due":"2026-07-27","end":None,"description":"Capture defects, performance issues, usability gaps, and improvement opportunities identified during field testing for prioritized remediation."},
            {"title":"Develop Standard Operating Procedures","cat":"Core Rollout","typ":"SOPs & Training","comp":None,"st":"Not Started","pri":HIGH,"env":PROD,"start":"2026-07-27","due":"2026-08-24","end":None,"description":"Create SOPs covering daily operational workflows, data refresh schedules, user management procedures, and escalation paths."},
            {"title":"Create Training Materials & Instructional Videos","cat":"Core Rollout","typ":"SOPs & Training","comp":None,"st":"Not Started","pri":HIGH,"env":PROD,"start":"2026-08-03","due":"2026-09-01","end":None,"description":"Develop stakeholder-specific training materials and instructional videos covering portal navigation, key features, and common workflows."},
            {"title":"Configure Access Control for Beta User Group","cat":"Core Rollout","typ":"Beta Deployment","comp":"Frontend","st":"Not Started","pri":HIGH,"env":PROD,"start":"2026-08-24","due":"2026-09-14","end":None,"description":"Configure Entra ID groups and role assignments to restrict beta access to a selected group of stakeholders across each portal."},
            {"title":"Deploy Beta Release to Selected Users","cat":"Core Rollout","typ":"Beta Deployment","comp":None,"st":"Not Started","pri":HIGH,"env":PROD,"start":"2026-09-14","due":"2026-09-28","end":None,"description":"Deploy the beta release to the production environment with access limited to the approved beta user group. Monitor for stability."},
            {"title":"Monitor System Usage, Performance & User Adoption","cat":"Core Rollout","typ":"Beta Deployment","comp":None,"st":"Not Started","pri":MED,"env":PROD,"start":"2026-09-28","due":"2026-10-26","end":None,"description":"Track system usage patterns, performance metrics, and user adoption rates during the beta period to inform go-live readiness."},
            {"title":"Collect & Analyze User Feedback","cat":"Core Rollout","typ":"Beta Deployment","comp":None,"st":"Not Started","pri":MED,"env":PROD,"start":"2026-09-28","due":"2026-10-26","end":None,"description":"Gather structured feedback from beta users on usability, missing features, data accuracy, and workflow effectiveness. Prioritize findings for remediation."},
            {"title":"Finalize Ticketing System for User Support & Issue Tracking","cat":"Core Rollout","typ":"Support Setup","comp":None,"st":"Not Started","pri":MED,"env":PROD,"start":"2026-09-07","due":"2026-10-05","end":None,"description":"Configure the ticketing system for end-user issue reporting, support request tracking, and development team triage."},
            {"title":"Establish Ongoing Support & Issue Resolution Process","cat":"Core Rollout","typ":"Support Setup","comp":None,"st":"Not Started","pri":MED,"env":PROD,"start":"2026-10-05","due":"2026-10-26","end":None,"description":"Define the support model for production: response time targets, escalation paths, triage workflow, and handoff procedures between support and development."},
            {"title":"Finalize Web Interface Views for Production","cat":"Core Rollout","typ":"Production Release","comp":"Frontend","st":"Not Started","pri":HIGH,"env":PROD,"start":"2026-10-26","due":"2026-11-16","end":None,"description":"Complete final UI polish, resolve all outstanding usability issues from beta feedback, and ensure all portal views are production-ready."},
            {"title":"Deploy Fully Functional Application to Production","cat":"Core Rollout","typ":"Production Release","comp":None,"st":"Not Started","pri":CRIT,"env":PROD,"start":"2026-11-16","due":"2026-12-01","end":None,"description":"Full production deployment removing beta access restrictions. All stakeholder portals, API endpoints, and ETL pipelines operational with production data."},
            {"title":"Confirm Production Stability & Transition to Maintenance","cat":"Core Rollout","typ":"Production Release","comp":None,"st":"Not Started","pri":HIGH,"env":PROD,"start":"2026-12-01","due":"2026-12-22","end":None,"description":"Monitor production stability post-launch, confirm all SLIs are within targets, and formally transition to the ongoing support and maintenance model."},

            # ── ENHANCEMENTS & OPTIMIZATIONS (11) ── Jan 19 → Dec 22 ──
            {"title":"Project Documentation & READMEs","cat":"Enhancements & Optimizations","typ":"Documentation","comp":None,"st":"Complete","pri":MED,"env":DEV,"start":"2026-01-19","due":"2026-03-11","end":"2026-03-11","description":"Comprehensive project documentation including repository READMEs for all three components, architecture overview, and development guides."},
            {"title":"Production Operational Documentation","cat":"Enhancements & Optimizations","typ":"Documentation","comp":None,"st":"Not Started","pri":HIGH,"env":PROD,"start":"2026-09-01","due":"2026-10-13","end":None,"description":"Production-grade operational documentation including architecture docs, deployment runbooks, disaster recovery playbook, and incident response playbook."},
            {"title":"Security Testing & Load Testing Documentation","cat":"Enhancements & Optimizations","typ":"Documentation","comp":None,"st":"Not Started","pri":MED,"env":PROD,"start":"2026-10-13","due":"2026-11-10","end":None,"description":"Consolidated documentation of all security testing engagements, load testing results, capacity projections, and remediation logs."},
            {"title":"Dev Environment Load Testing Program","cat":"Enhancements & Optimizations","typ":"Performance Testing","comp":None,"st":"Not Started","pri":HIGH,"env":DEV,"start":"2026-05-04","due":"2026-06-15","end":None,"description":"Establish load testing strategy, tooling, and baseline performance metrics in the dev environment before production testing."},
            {"title":"Production Load Testing Program","cat":"Enhancements & Optimizations","typ":"Performance Testing","comp":None,"st":"Not Started","pri":HIGH,"env":PROD,"start":"2026-08-17","due":"2026-09-28","end":None,"description":"Execute production load testing program, establish performance baselines, identify bottlenecks, and validate capacity for expected user volumes."},
            {"title":"Security Testing Suite (SAST, DAST, pen test, SCA, auth & API review)","cat":"Enhancements & Optimizations","typ":"Security Testing","comp":None,"st":"Not Started","pri":CRIT,"env":PROD,"start":"2026-06-15","due":"2026-08-17","end":None,"description":"Comprehensive security testing program including static analysis, dynamic analysis, penetration testing, dependency scanning, authentication review, and API security assessment."},
            {"title":"Production Monitoring, Logging & Alerting","cat":"Enhancements & Optimizations","typ":"Production Hardening","comp":None,"st":"Not Started","pri":HIGH,"env":PROD,"start":"2026-09-01","due":"2026-10-13","end":None,"description":"Implement production monitoring stack with centralized logging, health check endpoints, alerting rules, and dashboards for all services."},
            {"title":"Production Hardening (secrets, WAF, CSP, backups, CI/CD)","cat":"Enhancements & Optimizations","typ":"Production Hardening","comp":None,"st":"Not Started","pri":HIGH,"env":PROD,"start":"2026-10-13","due":"2026-11-17","end":None,"description":"Production hardening pass: secrets management via 1Password, WAF configuration, content security policy, automated backups, and CI/CD pipeline setup."},
            {"title":"SLIs/SLOs, Data Migration & Capacity Planning","cat":"Enhancements & Optimizations","typ":"Operational Readiness","comp":None,"st":"Not Started","pri":MED,"env":PROD,"start":"2026-10-26","due":"2026-11-23","end":None,"description":"Define service level indicators and objectives, plan data migration strategy, and establish capacity projections for the first 6-12 months."},
            {"title":"Stakeholder Demo & Go-Live Readiness","cat":"Enhancements & Optimizations","typ":"Operational Readiness","comp":None,"st":"Not Started","pri":MED,"env":PROD,"start":"2026-11-23","due":"2026-12-08","end":None,"description":"Conduct stakeholder demonstrations across all portals, gather final sign-off, and validate go-live readiness checklist."},
            {"title":"Helpdesk Training & End-User Support Coordination","cat":"Enhancements & Optimizations","typ":"Operational Readiness","comp":None,"st":"Not Started","pri":MED,"env":PROD,"start":"2026-12-01","due":"2026-12-22","end":None,"description":"Coordinate with IT helpdesk for production launch support: training materials, troubleshooting guides, escalation paths, and development team contacts."},

            # ── EXPANSION (12) ── Jan 5, 2027 → Apr 12, 2027 ── post-launch ──
            {"title":"XtractOne Integration","cat":"Expansion","typ":"System Integration","comp":None,"st":"Not Started","pri":MED,"env":PROD,"start":"2027-01-05","due":"2027-02-02","end":None,"description":"Integrate XtractOne access control data into the mySphere platform for unified entry tracking and security analytics."},
            {"title":"Ticketmaster Integration","cat":"Expansion","typ":"System Integration","comp":None,"st":"Not Started","pri":MED,"env":PROD,"start":"2027-01-19","due":"2027-02-16","end":None,"description":"Integrate Ticketmaster event and ticketing data for venue-wide event correlation and operational planning."},
            {"title":"Continuous Data Discovery","cat":"Expansion","typ":"System Integration","comp":None,"st":"Not Started","pri":LOW,"env":PROD,"start":"2027-02-02","due":"2027-04-12","end":None,"description":"Ongoing identification and evaluation of new data sources across the organization for potential integration into the platform."},
            {"title":"Notification Engine Expansion","cat":"Expansion","typ":"Feature Expansion","comp":None,"st":"Not Started","pri":MED,"env":PROD,"start":"2027-01-05","due":"2027-02-02","end":None,"description":"Expand the notification engine beyond security announcements to support cross-department alerts, scheduling updates, and operational notices."},
            {"title":"Inventory Tracking Module","cat":"Expansion","typ":"Feature Expansion","comp":None,"st":"Not Started","pri":MED,"env":PROD,"start":"2027-02-02","due":"2027-03-09","end":None,"description":"New micro-service for tracking equipment, supplies, and asset inventory across venue operations."},
            {"title":"Training Tracking Module","cat":"Expansion","typ":"Feature Expansion","comp":None,"st":"Not Started","pri":MED,"env":PROD,"start":"2027-02-16","due":"2027-03-23","end":None,"description":"New micro-service for tracking employee training completion, certifications, and compliance requirements."},
            {"title":"User Record & Access Management","cat":"Expansion","typ":"Feature Expansion","comp":None,"st":"Not Started","pri":LOW,"env":PROD,"start":"2027-03-09","due":"2027-04-05","end":None,"description":"Self-service user profile management and access request workflows integrated with Entra ID."},
            {"title":"Decision Making Tools","cat":"Expansion","typ":"Executive Analytics","comp":None,"st":"Not Started","pri":MED,"env":PROD,"start":"2027-01-19","due":"2027-02-23","end":None,"description":"Executive decision support tools providing scenario modeling, trend analysis, and operational impact projections."},
            {"title":"Venue-Wide Reporting & Insights","cat":"Expansion","typ":"Executive Analytics","comp":None,"st":"Not Started","pri":MED,"env":PROD,"start":"2027-02-16","due":"2027-03-23","end":None,"description":"Cross-department reporting dashboards providing venue-wide operational insights, staffing efficiency, and event performance metrics."},
            {"title":"KPI Tracking Dashboard","cat":"Expansion","typ":"Executive Analytics","comp":None,"st":"Not Started","pri":MED,"env":PROD,"start":"2027-03-01","due":"2027-04-05","end":None,"description":"Real-time KPI tracking dashboard for executives with configurable metrics, trend visualization, and alerting thresholds."},
            {"title":"Operational Overhead & Bottleneck Assessment","cat":"Expansion","typ":"Scalability Assessment","comp":None,"st":"Not Started","pri":LOW,"env":PROD,"start":"2027-01-05","due":"2027-02-09","end":None,"description":"Assess operational overhead as the platform scales, identify system workflow bottlenecks, and establish performance benchmarks."},
            {"title":"Headcount & Resource Planning for Platform Maintenance","cat":"Expansion","typ":"Scalability Assessment","comp":None,"st":"Not Started","pri":LOW,"env":PROD,"start":"2027-02-09","due":"2027-03-09","end":None,"description":"Determine additional developer headcount and resource requirements needed to sustain platform growth, maintenance, and feature velocity."},
        ]
        # fmt: on

        for td in T:
            cat = category_map[td["cat"]]
            typ = type_map.get(td["typ"])
            st = status_map[td["st"]]
            comp = component_map.get(td["comp"]) if td.get("comp") else None
            session.add(Task(
                project_id=project.id, category_id=cat.id,
                type_id=typ.id if typ else None, status_id=st.id,
                component_id=comp.id if comp else None,
                title=td["title"], description=td.get("description"),
                priority=td.get("pri", MED), environment=td.get("env"),
                start_date=_d(td.get("start")), due_date=_d(td.get("due")),
                completed_at=_dt(td.get("end")),
            ))

        session.commit()

        total = len(T)
        by_phase: dict[str, int] = {}
        for t in T:
            by_phase[t["cat"]] = by_phase.get(t["cat"], 0) + 1
        logger.info("Seeded %d executive roadmap tasks:", total)
        for phase, count in by_phase.items():
            logger.info("  %s: %d tasks", phase, count)
        logger.info("Executive roadmap seed complete.")


if __name__ == "__main__":
    seed()