"""
Seed production-environment tasks for the mySphere project.

Mirrors the test-environment task structure, then adds:
  - Full load-testing capabilities
  - InfoSec security testing requests (SAST, DAST, pen test, SCA, auth review, API assessment)
  - Production-readiness tasks (monitoring, alerting, DR, backups, secrets, CI/CD, etc.)
  - Production documentation (runbooks, playbooks, architecture docs)

All tasks are created with status_id=1 (Not Started) since no production progress exists yet.
"""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

# Resolve DB path relative to app/mock_db/ (one level up from app/seed/ to app/, then into mock_db/)
_SCRIPT_DIR = Path(__file__).resolve().parent
_APP_DIR = _SCRIPT_DIR.parent
DB_PATH = str(_APP_DIR / "mock_db" / "qc_builder_mock_db.sqlite3")

# Reference IDs from the existing seed data
PROJECT_ID = 1
# Status IDs
NOT_STARTED = 1
# Category IDs
DEV = 1
COMM = 2
DOCS = 3
# Type IDs (within Development category)
TYPE_NEW_ETL = 1
TYPE_NEW_API_ROUTE = 2
TYPE_NEW_FRONTEND = 3
TYPE_BUG_FIX = 4
TYPE_REFACTOR = 5
TYPE_INFRA = 6
# Type IDs (within Communication category)
TYPE_CROSS_TEAM = 7
TYPE_STAKEHOLDER_UPDATE = 8
TYPE_ACCESS_REQUEST = 9
TYPE_VENDOR = 10
# Type IDs (within Documentation category)
TYPE_README = 11
TYPE_TECH_DOC = 12
TYPE_PLAYBOOK = 13
TYPE_PROGRAM_DOC = 14
TYPE_RUNBOOK = 15
# Component IDs
COMP_ETL = 1
COMP_API = 2
COMP_FRONTEND = 3

ENV = "PROD"
NOW = datetime.now(UTC).isoformat()

# fmt: off
tasks = [
    # =========================================================================
    # MIRRORED FROM TEST — Infrastructure / Environment Setup (no component)
    # =========================================================================
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Stand up production environment",
        "description": (
            "Provision and configure the production environment once the test environment "
            "is fully validated and InfoSec-cleared. Must include hardened OS, production-grade "
            "TLS, firewall rules, and network segmentation before any services are deployed."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "InfoSec security scan of production environment VM",
        "description": (
            "Have InfoSec perform a full security scan of the production VM prior to any "
            "deployment. Must satisfy all organizational security policies and hardening "
            "standards. No services may go live until the scan is passed."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Address InfoSec action items from production environment scan",
        "description": (
            "Remediate all findings from the InfoSec production environment scan. "
            "Every critical and high-severity item must be resolved before production "
            "deployment is authorized."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Connect services to production database",
        "description": (
            "Configure all production services to use the production database connection "
            "strings. Verify schema parity with test, confirm write permissions, and validate "
            "connection pooling and failover settings."
        ),
    },

    # =========================================================================
    # MIRRORED FROM TEST — Communication / Provisioning Requests (no component)
    # =========================================================================
    {
        "category_id": COMM, "type_id": TYPE_ACCESS_REQUEST, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Request production-signed TLS certificates",
        "description": (
            "Request properly signed TLS certificates for the production environment from "
            "the certificate authority team. Required before any HTTPS traffic is served "
            "in production."
        ),
    },
    {
        "category_id": COMM, "type_id": TYPE_ACCESS_REQUEST, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Request VM provisioning for production environment",
        "description": (
            "Request infrastructure team to provision the production VM with the required "
            "compute, memory, and storage specifications. Must meet production SLA requirements."
        ),
    },
    {
        "category_id": COMM, "type_id": TYPE_ACCESS_REQUEST, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Request database provisioning for production environment",
        "description": (
            "Request DBA team to provision the production database instance, create schemas "
            "and tables, configure replication, and grant application service account permissions."
        ),
    },
    {
        "category_id": COMM, "type_id": TYPE_CROSS_TEAM, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Coordinate with InfoSec for production environment VM scan",
        "description": (
            "Schedule and coordinate the InfoSec security scan of the production VM. "
            "Ensure the VM is in its deployment-ready state before the scan is performed."
        ),
    },
    {
        "category_id": COMM, "type_id": TYPE_CROSS_TEAM, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Coordinate with InfoSec on scan action items before production go-live",
        "description": (
            "After the production scan, coordinate with InfoSec to understand, prioritize, "
            "and schedule remediation of all findings. All critical items must be resolved "
            "before production go-live."
        ),
    },

    # =========================================================================
    # MIRRORED FROM TEST — Component-Specific Deployment Tasks
    # =========================================================================
    {
        "category_id": DEV, "type_id": TYPE_REFACTOR, "status_id": NOT_STARTED,
        "component_id": COMP_ETL, "priority": "HIGH",
        "title": "Translate ETL pipelines to production environment",
        "description": (
            "Port all ETL pipeline families (EOD, WFR, EAP) into the production environment. "
            "Replace SQLite writers with the production database writer (MySQL/SQL Server). "
            "Validate data integrity against test environment outputs."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": COMP_API, "priority": "HIGH",
        "title": "Scaffold production environment API repo (mysphere-api-prod)",
        "description": (
            "Create the production API repository with hardened configuration, production "
            "database connection, environment-specific settings, and CI/CD integration. "
            "Mirror the test repo structure with production-grade defaults."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_REFACTOR, "status_id": NOT_STARTED,
        "component_id": COMP_API, "priority": "HIGH",
        "title": "Translate API modules to production environment architecture",
        "description": (
            "Port the FastAPI backend and all domain routers from the test environment into "
            "the production repo. Ensure all environment variables, connection strings, and "
            "secrets reference production infrastructure."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": COMP_FRONTEND, "priority": "HIGH",
        "title": "Scaffold production environment frontend repo (mysphere-prod)",
        "description": (
            "Create the production frontend repository with production build configuration, "
            "optimized bundles, CSP headers, and environment-specific API endpoints."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_REFACTOR, "status_id": NOT_STARTED,
        "component_id": COMP_FRONTEND, "priority": "HIGH",
        "title": "Translate Angular frontend modules for production environment",
        "description": (
            "Migrate the Angular frontend from the test Nx monorepo into the production build. "
            "Strip all mock/fake data systems, ensure Entra ID SSO targets production tenant, "
            "and verify all API endpoints point to production."
        ),
    },

    # =========================================================================
    # LOAD TESTING
    # =========================================================================
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Define load testing strategy and acceptance criteria",
        "description": (
            "Document the load testing strategy including target concurrent users, expected "
            "request throughput, acceptable response time thresholds (p50, p95, p99), and "
            "error rate ceilings. Define pass/fail criteria for production go-live."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Set up load testing infrastructure",
        "description": (
            "Select and configure a load testing tool (e.g. k6, Locust, or JMeter). "
            "Set up the test runner environment, reporting dashboards, and result storage. "
            "Ensure load tests can target the production environment without affecting real users."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": COMP_API, "priority": "HIGH",
        "title": "Develop API load test scripts",
        "description": (
            "Write load test scripts covering all critical API endpoints: authentication, "
            "employee directory, PTO operations, EAP viewer, calendars, notifications, and "
            "post orders. Include ramp-up, sustained load, and spike test scenarios."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": COMP_FRONTEND, "priority": "MEDIUM",
        "title": "Develop frontend performance test scripts",
        "description": (
            "Create performance test scripts for key frontend user flows: SSO login, "
            "portal navigation, dashboard rendering, and data-heavy views (EAP, calendars). "
            "Measure Core Web Vitals (LCP, FID, CLS) under load."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Execute full load test suite and document results",
        "description": (
            "Run the complete load test suite against the production environment in a "
            "controlled window. Document results against acceptance criteria including "
            "throughput, latency percentiles, error rates, and resource utilization."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_BUG_FIX, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Address performance bottlenecks identified during load testing",
        "description": (
            "Investigate and resolve any performance issues surfaced by load testing. "
            "May include query optimization, connection pool tuning, caching strategy, "
            "or infrastructure scaling. Re-run affected tests to confirm resolution."
        ),
    },

    # =========================================================================
    # INFOSEC SECURITY TESTING REQUESTS
    # =========================================================================
    {
        "category_id": COMM, "type_id": TYPE_CROSS_TEAM, "status_id": NOT_STARTED,
        "component_id": None, "priority": "CRITICAL",
        "title": "Request SAST (Static Application Security Testing) scan",
        "description": (
            "Request InfoSec to perform static analysis on all application source code "
            "(ETL pipelines, FastAPI backend, Angular frontend). SAST identifies "
            "vulnerabilities such as injection flaws, hardcoded secrets, insecure "
            "deserialization, and unsafe coding patterns without executing the application."
        ),
    },
    {
        "category_id": COMM, "type_id": TYPE_CROSS_TEAM, "status_id": NOT_STARTED,
        "component_id": None, "priority": "CRITICAL",
        "title": "Request DAST (Dynamic Application Security Testing) scan",
        "description": (
            "Request InfoSec to perform dynamic analysis against the running production "
            "application. DAST simulates external attacks to identify runtime vulnerabilities "
            "including XSS, SQL injection, CSRF, broken authentication, security "
            "misconfigurations, and insecure HTTP headers."
        ),
    },
    {
        "category_id": COMM, "type_id": TYPE_CROSS_TEAM, "status_id": NOT_STARTED,
        "component_id": None, "priority": "CRITICAL",
        "title": "Request penetration testing engagement",
        "description": (
            "Request InfoSec to conduct a manual penetration test of the mySphere application. "
            "Pen testers should target authentication flows (Entra ID SSO), role-based access "
            "control boundaries between portals (executive, security manager, HSE, developer), "
            "API authorization, session management, and data exposure across role boundaries."
        ),
    },
    {
        "category_id": COMM, "type_id": TYPE_CROSS_TEAM, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Request dependency and SCA vulnerability scan",
        "description": (
            "Request InfoSec to run Software Composition Analysis (SCA) across all "
            "repositories to identify known CVEs in third-party dependencies (Python packages, "
            "npm modules, Angular libraries). All critical and high-severity CVEs must be "
            "resolved or risk-accepted before production go-live."
        ),
    },
    {
        "category_id": COMM, "type_id": TYPE_CROSS_TEAM, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Request authentication and authorization security review",
        "description": (
            "Request InfoSec to review the Entra ID SSO integration, JWT token handling, "
            "role-based access control implementation, and session management. Should verify "
            "that role escalation is not possible, tokens are properly validated, and session "
            "timeouts are enforced per organizational policy."
        ),
    },
    {
        "category_id": COMM, "type_id": TYPE_CROSS_TEAM, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Request API security assessment",
        "description": (
            "Request InfoSec to assess all 11 API domain routers for OWASP API Security "
            "Top 10 risks: broken object-level authorization, broken authentication, "
            "excessive data exposure, lack of rate limiting, broken function-level "
            "authorization, mass assignment, and injection vulnerabilities."
        ),
    },

    # =========================================================================
    # INFOSEC — Remediation Tasks
    # =========================================================================
    {
        "category_id": DEV, "type_id": TYPE_BUG_FIX, "status_id": NOT_STARTED,
        "component_id": None, "priority": "CRITICAL",
        "title": "Remediate findings from SAST scan",
        "description": (
            "Address all critical and high-severity findings from the SAST scan. "
            "Fix insecure coding patterns, remove hardcoded secrets, resolve injection "
            "risks, and re-scan to confirm remediation."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_BUG_FIX, "status_id": NOT_STARTED,
        "component_id": None, "priority": "CRITICAL",
        "title": "Remediate findings from DAST scan",
        "description": (
            "Address all critical and high-severity findings from the DAST scan. "
            "Fix runtime vulnerabilities including XSS, CSRF, insecure headers, "
            "and misconfigurations. Re-scan to confirm remediation."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_BUG_FIX, "status_id": NOT_STARTED,
        "component_id": None, "priority": "CRITICAL",
        "title": "Remediate findings from penetration test",
        "description": (
            "Address all critical and high-severity findings from the penetration test. "
            "Focus on authentication bypass, privilege escalation, data leakage across "
            "role boundaries, and any other exploitable vulnerabilities. Request re-test "
            "of remediated items."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_BUG_FIX, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Remediate critical CVEs from dependency scan",
        "description": (
            "Upgrade or patch all third-party dependencies with critical or high-severity "
            "CVEs identified by the SCA scan. Where upgrades introduce breaking changes, "
            "document the migration path and test thoroughly."
        ),
    },

    # =========================================================================
    # PRODUCTION READINESS — Operations & Observability
    # =========================================================================
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Configure production monitoring and alerting",
        "description": (
            "Set up application and infrastructure monitoring for the production environment. "
            "Include health check endpoints for all services, CPU/memory/disk utilization "
            "alerts, API response time monitoring, error rate thresholds, and database "
            "connection pool metrics."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Set up production logging and log aggregation",
        "description": (
            "Configure centralized logging for all production services (ETL, API, frontend). "
            "Ensure structured log formats, appropriate log levels, log rotation, and "
            "retention policies. Sensitive data must be masked in all log output."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Configure secrets management for production",
        "description": (
            "Move all production secrets (database credentials, API keys, Entra ID client "
            "secrets, TLS private keys) into a secrets manager. Remove any hardcoded secrets "
            "from configuration files and environment variables. Rotate all initial credentials."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Configure production backup strategy",
        "description": (
            "Implement automated database backups with defined RPO (Recovery Point Objective). "
            "Configure backup schedules, retention periods, offsite storage, and verify "
            "backup restoration process end-to-end."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": None, "priority": "MEDIUM",
        "title": "Define SLIs and SLOs for production services",
        "description": (
            "Define Service Level Indicators (SLIs) and Service Level Objectives (SLOs) "
            "for each production service. Include availability targets, latency thresholds, "
            "error budgets, and throughput baselines. Align with stakeholder expectations "
            "and document in the production architecture doc."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Production deployment CI/CD pipeline",
        "description": (
            "Set up the CI/CD pipeline for production deployments. Include automated testing "
            "gates, security scan integration, staged rollout capability, and one-click "
            "rollback. Deployment to production should require explicit approval."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": None, "priority": "MEDIUM",
        "title": "Configure production web application firewall (WAF) rules",
        "description": (
            "Configure WAF rules for the production environment to protect against common "
            "web attacks (OWASP Top 10). Include rate limiting rules for API endpoints, "
            "bot protection, and IP-based access controls as needed."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": None, "priority": "MEDIUM",
        "title": "Implement Content Security Policy and security headers",
        "description": (
            "Configure production security headers including Content-Security-Policy, "
            "Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options, "
            "Referrer-Policy, and Permissions-Policy. Validate headers do not break "
            "application functionality."
        ),
    },
    {
        "category_id": DEV, "type_id": TYPE_INFRA, "status_id": NOT_STARTED,
        "component_id": None, "priority": "MEDIUM",
        "title": "Production data migration and validation",
        "description": (
            "Plan and execute the data migration from test to production. Validate data "
            "integrity post-migration by comparing record counts, checksums, and spot-checking "
            "critical data sets. Document the migration procedure for repeatability."
        ),
    },

    # =========================================================================
    # PRODUCTION READINESS — Communication / Coordination
    # =========================================================================
    {
        "category_id": COMM, "type_id": TYPE_CROSS_TEAM, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Final production go/no-go readiness review",
        "description": (
            "Conduct a cross-functional readiness review with development, InfoSec, "
            "infrastructure, and stakeholders. Walk through the production readiness "
            "checklist, confirm all blockers are resolved, and obtain sign-off for go-live."
        ),
    },
    {
        "category_id": COMM, "type_id": TYPE_STAKEHOLDER_UPDATE, "status_id": NOT_STARTED,
        "component_id": None, "priority": "MEDIUM",
        "title": "Stakeholder demo of production environment before go-live",
        "description": (
            "Present the production environment to key stakeholders (executive, security, "
            "HSE, developer teams) for final review. Demonstrate key workflows, SSO login, "
            "role-based access, and data accuracy before authorizing go-live."
        ),
    },
    {
        "category_id": COMM, "type_id": TYPE_CROSS_TEAM, "status_id": NOT_STARTED,
        "component_id": None, "priority": "MEDIUM",
        "title": "Coordinate helpdesk and end-user support training",
        "description": (
            "Coordinate with IT helpdesk and support teams to prepare for production launch. "
            "Provide training materials, common troubleshooting steps, escalation paths, "
            "and contact information for the development team."
        ),
    },
    {
        "category_id": COMM, "type_id": TYPE_ACCESS_REQUEST, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Request production DNS and network configuration",
        "description": (
            "Request networking team to configure production DNS records, load balancer "
            "rules, and firewall policies. Ensure the production URL is resolvable and "
            "traffic is properly routed to the application servers."
        ),
    },

    # =========================================================================
    # PRODUCTION DOCUMENTATION
    # =========================================================================
    {
        "category_id": DOCS, "type_id": TYPE_TECH_DOC, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Production environment architecture document",
        "description": (
            "Document the production environment architecture including network topology, "
            "server specifications, database configuration, TLS setup, service dependencies, "
            "and data flow diagrams. Should serve as the canonical reference for the "
            "production deployment."
        ),
    },
    {
        "category_id": DOCS, "type_id": TYPE_RUNBOOK, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Production deployment runbook",
        "description": (
            "Step-by-step operational procedure for deploying to production. Include "
            "pre-deployment checks, deployment commands, post-deployment validation, "
            "rollback procedures, and contact information for each service owner."
        ),
    },
    {
        "category_id": DOCS, "type_id": TYPE_PLAYBOOK, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Disaster recovery playbook",
        "description": (
            "Document disaster recovery procedures including RTO/RPO targets, backup "
            "restoration steps, database failover process, service recovery order, "
            "and communication plan for outages."
        ),
    },
    {
        "category_id": DOCS, "type_id": TYPE_PLAYBOOK, "status_id": NOT_STARTED,
        "component_id": None, "priority": "HIGH",
        "title": "Incident response playbook",
        "description": (
            "Define the incident response process for production issues. Include severity "
            "classification, escalation paths, communication channels, on-call responsibilities, "
            "post-incident review process, and templates for status updates."
        ),
    },
    {
        "category_id": DOCS, "type_id": TYPE_TECH_DOC, "status_id": NOT_STARTED,
        "component_id": None, "priority": "MEDIUM",
        "title": "Security testing results and remediation log",
        "description": (
            "Consolidated document tracking all security testing engagements (SAST, DAST, "
            "pen test, SCA, auth review, API assessment), their findings, remediation "
            "actions taken, and verification status. Serves as the audit trail for "
            "InfoSec compliance."
        ),
    },
    {
        "category_id": DOCS, "type_id": TYPE_TECH_DOC, "status_id": NOT_STARTED,
        "component_id": None, "priority": "MEDIUM",
        "title": "Load testing results and capacity plan",
        "description": (
            "Document load testing methodology, results, performance baselines, and "
            "capacity projections. Include recommendations for scaling thresholds and "
            "resource planning for the next 6-12 months."
        ),
    },
]
# fmt: on


def seed_production_tasks():
    if not Path(DB_PATH).exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        print(f"  Script location: {_SCRIPT_DIR}")
        print(f"  Resolved app dir: {_APP_DIR}")
        print("  Ensure qc_builder_mock_db.sqlite3 is in app/mock_db/.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get current max ID
    cur.execute("SELECT MAX(id) FROM tasks")
    max_id = cur.fetchone()[0] or 0

    inserted = 0
    for t in tasks:
        cur.execute(
            """
            INSERT INTO tasks (
                project_id, category_id, type_id, status_id, component_id,
                title, description, assignee, priority, environment,
                start_date, due_date, completed_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                PROJECT_ID,
                t["category_id"],
                t["type_id"],
                t["status_id"],
                t["component_id"],
                t["title"],
                t["description"],
                None,       # assignee
                t["priority"],
                ENV,
                None,       # start_date
                None,       # due_date
                None,       # completed_at
                NOW,
                NOW,
            ),
        )
        inserted += 1

    conn.commit()

    # Print summary
    cur.execute("SELECT COUNT(*) FROM tasks WHERE environment = 'PROD'")
    total_prod = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks")
    total_all = cur.fetchone()[0]

    print(f"Inserted {inserted} PROD tasks (IDs {max_id + 1}–{max_id + inserted})")
    print(f"Total PROD tasks: {total_prod}")
    print(f"Total tasks in database: {total_all}")

    # Breakdown
    print("\n--- PROD Task Breakdown ---")
    cur.execute("""
        SELECT
            CASE category_id
                WHEN 1 THEN 'Development'
                WHEN 2 THEN 'Communication'
                WHEN 3 THEN 'Documentation'
            END as category,
            COUNT(*) as count
        FROM tasks WHERE environment = 'PROD'
        GROUP BY category_id ORDER BY category_id
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    print("\n--- By Priority ---")
    cur.execute("""
        SELECT priority, COUNT(*) FROM tasks
        WHERE environment = 'PROD' GROUP BY priority ORDER BY priority
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    print("\n--- By Component ---")
    cur.execute("""
        SELECT
            COALESCE(pc.name, 'Infrastructure / Cross-Cutting') as comp,
            COUNT(*) as count
        FROM tasks t
        LEFT JOIN project_components pc ON t.component_id = pc.id
        WHERE t.environment = 'PROD'
        GROUP BY t.component_id ORDER BY t.component_id
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()


if __name__ == "__main__":
    seed_production_tasks()