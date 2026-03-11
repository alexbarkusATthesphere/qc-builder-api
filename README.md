# QC Builder API

A FastAPI-based REST API for managing project templates, task workflows, and team-level tracking conventions. Serves as the backend for the QC Builder internal dashboard. Designed to be flexible enough that different teams can define their own task categories, types, and status workflows without code changes.

> **Audience:** Developers of all levels working on or integrating with this API.

---

## Quick Start

### Prerequisites

- Python 3.11+
- SQLite (bundled with Python, no separate install needed)

### Setup

```bash
cd qc-builder-api

# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .

# Copy environment template
cp .env.example .env
# Edit .env with your configuration (see Configuration section)
```

### Run the API

```bash
# Development (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python -m app.main
```

### Interactive Docs

Once running, API documentation is available at:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON:** [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)

### Seed Data

To populate the database with a starter template and sample project:

```bash
python -m app.seed.seed_web_team_template
```

This creates a "Web Development" template with categories (Development, Communication, Documentation), task types, statuses, and a sample "SWIKI" project with components and example tasks. Useful for local development and for validating the data model against real work.

---

## Data Model

The API is built around a configurable hierarchy that lets each team define their own project structure.

### Entity Hierarchy

```
Template
 ├── StatusDefinition[]       Ordered workflow states (e.g. Not Started -> Complete)
 ├── TaskCategory[]           Grouping layer (e.g. Development, Communication)
 │    └── TaskType[]          Specific work kinds (e.g. New ETL Pipeline, README)
 │
Project (uses a Template)
 ├── ProjectComponent[]       Optional subsystems (e.g. ETL, API, Frontend)
 └── Task[]
      ├── -> TaskCategory
      ├── -> TaskType (optional)
      ├── -> StatusDefinition
      ├── -> ProjectComponent (optional)
      ├── TaskComment[]
      └── TaskHistory[]       Automatic audit log of field changes
```

### How the hierarchy works

**Templates** are the configuration layer. A template defines the vocabulary of statuses, categories, and types that are available to any project using it. When a team creates a new project, they pick a template and immediately inherit its full workflow. This means teams define their conventions once and reuse them across projects.

**Task categories** are the high-level groupings within a template. For our web team, these are "Development", "Communication", and "Documentation". Another team using a different template might have "Procurement", "Vendor Management", and "Compliance" instead.

**Task types** are the specific kinds of work within a category. Under "Development" we have things like "New ETL Pipeline", "New API Route", and "Bug Fix". Under "Documentation" we have "README", "Playbook", "Technical Doc", etc. Types are optional on tasks, so not every task needs one.

**Project components** are defined per project, not per template. Our SWIKI project has ETL Pipelines, API, and Frontend as components, but another project using the same "Web Development" template might have completely different modules. Components serve as a first-class filter dimension on tasks.

**Status definitions** are also template-level. Each status has a `display_order` for rendering (kanban columns, progress bars), an `is_default` flag (assigned automatically on task creation), and an `is_terminal` flag (marks completion states like "Complete" or "Cancelled"). This lets the system distinguish active from finished tasks without hardcoding status names.

---

## API Domains

All endpoints are mounted under `/api/v1/`. The API exposes three domain routers.

### Templates (`/api/v1/templates`)

Template CRUD and management of the configurable children: statuses, categories, and types.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | List all templates (filter: `is_active`) |
| `POST` | `/` | Create a template |
| `GET` | `/{template_id}` | Get template with all children (categories, types, statuses) |
| `PATCH` | `/{template_id}` | Update template metadata |
| `DELETE` | `/{template_id}` | Soft-delete (set `is_active=false`) |

**Statuses**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/{template_id}/statuses` | List statuses for a template |
| `POST` | `/{template_id}/statuses` | Create a status definition |
| `PATCH` | `/{template_id}/statuses/{status_id}` | Update status (name, color, order) |
| `DELETE` | `/{template_id}/statuses/{status_id}` | Delete (only if no tasks reference it) |
| `PUT` | `/{template_id}/statuses/reorder` | Bulk reorder statuses |

**Categories**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/{template_id}/categories` | List categories for a template |
| `POST` | `/{template_id}/categories` | Create a category |
| `PATCH` | `/{template_id}/categories/{category_id}` | Update category |
| `DELETE` | `/{template_id}/categories/{category_id}` | Delete (only if no tasks reference it) |

**Types**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/{template_id}/categories/{category_id}/types` | List types in a category |
| `POST` | `/{template_id}/categories/{category_id}/types` | Create a type |
| `PATCH` | `/{template_id}/categories/{category_id}/types/{type_id}` | Update type |
| `DELETE` | `/{template_id}/categories/{category_id}/types/{type_id}` | Delete (only if unused) |

### Projects (`/api/v1/projects`)

Project CRUD and component management.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | List projects (filters: `status`, `template_id`, `owner`) |
| `POST` | `/` | Create a project |
| `GET` | `/{project_id}` | Get project with summary counts |
| `PATCH` | `/{project_id}` | Update project metadata |
| `DELETE` | `/{project_id}` | Archive project |

**Components**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/{project_id}/components` | List components |
| `POST` | `/{project_id}/components` | Create a component |
| `PATCH` | `/{project_id}/components/{component_id}` | Update component |
| `DELETE` | `/{project_id}/components/{component_id}` | Delete (only if no tasks reference it) |

Projects have a simple project-level status (`active`, `on_hold`, `complete`, `archived`) that is separate from the configurable task-level status definitions. A project's lifecycle is simpler and consistent across all teams.

### Tasks (`/api/v1/tasks`)

Task CRUD, filtering, comments, and change history.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | List tasks (filters: `project_id` (required), `category_id`, `type_id`, `status_id`, `component_id`, `assignee`, `priority`) |
| `POST` | `/` | Create a task |
| `GET` | `/{task_id}` | Get task with comments and recent history |
| `PATCH` | `/{task_id}` | Update task (auto-writes to task_history) |
| `DELETE` | `/{task_id}` | Delete task |
| `GET` | `/{task_id}/history` | Full change history for a task |
| `GET` | `/{task_id}/comments` | List comments on a task |
| `POST` | `/{task_id}/comments` | Add a comment |
| `PATCH` | `/{task_id}/comments/{comment_id}` | Edit a comment |
| `DELETE` | `/{task_id}/comments/{comment_id}` | Delete a comment |
| `GET` | `/summary` | Aggregate counts by status, category, component (filter: `project_id`) |

Task updates are automatically audited. The repository layer diffs the incoming patch against the current row and writes a `task_history` entry for every changed field. This happens at the data access layer so it is impossible to update a task without generating an audit trail.

---

## Architecture

### Layered Design

```
┌─────────────────────────────────────────────────────────────┐
│                         API Layer                            │
│   (FastAPI routers: templates, projects, tasks)              │
├─────────────────────────────────────────────────────────────┤
│                       Schema Layer                           │
│       (Pydantic models for request/response validation)      │
├─────────────────────────────────────────────────────────────┤
│                     Repository Layer                         │
│           (Data access: queries, filters, joins)             │
├─────────────────────────────────────────────────────────────┤
│                        ORM Layer                             │
│   (SQLModel: Template, Project, Task, StatusDefinition...)   │
├─────────────────────────────────────────────────────────────┤
│                        Database                              │
│            (SQLite now -> SQL Server later)                   │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```
qc-builder-api/
├── app/
│   ├── main.py                    FastAPI app entry point, lifespan, CORS
│   ├── alembic/
│   │   ├── env.py                 Alembic migration environment
│   │   └── versions/              Auto-generated migration scripts
│   ├── api/
│   │   ├── deps.py                Shared dependencies (DB session)
│   │   └── v1/
│   │       ├── router.py          Master router, aggregates all domain routers
│   │       ├── templates.py       Template, category, type, and status CRUD
│   │       ├── projects.py        Project CRUD, component management
│   │       └── tasks.py           Task CRUD, filtering, comments, history
│   ├── core/
│   │   ├── config.py              Pydantic Settings (env vars + .env)
│   │   ├── database.py            SQLModel engine + init_db()
│   │   └── logging.py             Logging configuration
│   ├── db/
│   │   └── session.py             get_session() dependency
│   ├── mock_db/
│   │   └── qc_builder_mock_db.sqlite3   Local dev datastore
│   ├── models/
│   │   ├── db/                    SQLModel ORM models
│   │   │   ├── template.py        Template, TaskCategory, TaskType, StatusDefinition
│   │   │   ├── project.py         Project, ProjectComponent
│   │   │   └── task.py            Task, TaskComment, TaskHistory
│   │   └── schemas/               Pydantic request/response schemas
│   │       ├── template.py
│   │       ├── project.py
│   │       └── task.py
│   ├── repositories/              Data access layer
│   │   ├── template_repo.py
│   │   ├── project_repo.py
│   │   └── task_repo.py
│   └── seed/
│       └── seed_web_team_template.py   Seeds starter template + sample project
├── tests/
├── .env.example                   Environment variable template
├── pyproject.toml                 Project metadata and dependencies
└── README.md
```

### Database

The API uses a local SQLite file (`app/mock_db/qc_builder_mock_db.sqlite3`) as the development datastore while the production Microsoft SQL Server database is being provisioned. The repository layer abstracts all queries through SQLModel/SQLAlchemy, so the migration to SQL Server requires changes only in `core/config.py` (connection string) and `database.py` (dialect-specific pragmas). No router or repository rewrites needed.

Alembic is configured for schema migrations:

```bash
# Generate a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Database Tables

**Template configuration tables:**

| Table | Description | Key Relationships |
|-------|-------------|-------------------|
| `templates` | Top-level config object. Defines the vocabulary for projects that use it. | Parent of statuses, categories |
| `status_definitions` | Ordered workflow states with display order, color, default/terminal flags. | FK to templates |
| `task_categories` | Grouping layer (e.g. Development, Communication, Documentation). | FK to templates |
| `task_types` | Specific work kinds within a category (e.g. New API Route, README). | FK to task_categories |

**Project tables:**

| Table | Description | Key Relationships |
|-------|-------------|-------------------|
| `projects` | A concrete initiative that uses a template's configuration. | FK to templates |
| `project_components` | Optional subsystems within a project (e.g. ETL, API, Frontend). | FK to projects |

**Task tables:**

| Table | Description | Key Relationships |
|-------|-------------|-------------------|
| `tasks` | The core work item. | FKs to projects, task_categories, task_types (nullable), status_definitions, project_components (nullable) |
| `task_comments` | Flat comment thread on a task. | FK to tasks |
| `task_history` | Automatic audit log of every field change on a task. | FK to tasks |

---

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Database (defaults to local mock_db path)
DATABASE_URL=sqlite:///app/mock_db/qc_builder_mock_db.sqlite3

# API Settings
API_V1_PREFIX=/api/v1
DEBUG=true
HOST=0.0.0.0
PORT=8000

# CORS (the Angular frontend runs on port 4200)
CORS_ORIGINS=["http://localhost:4200","http://127.0.0.1:4200"]
```

### Planned: SQL Server Migration

> **Status:** Pending, waiting on database provisioning.

The production target is Microsoft SQL Server. The migration path is:

1. Update the connection string in `core/config.py` to `mssql+pyodbc://...`
2. Add `pyodbc` to dependencies
3. Run Alembic migrations against the new target
4. Remove any SQLite-specific pragmas in `database.py`

### Planned: 1Password

The same 1Password migration planned for the SWIKI ETLs and API (see their respective READMEs) will apply here once provisioned. The `.env` file will be replaced with 1Password secret references or SDK-based resolution.

---

## Development

### Code Style

```bash
# Format code
ruff format .

# Lint and auto-fix
ruff check --fix .

# Type check
mypy app/
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Adding a New API Domain

1. Create the SQLModel ORM model in `app/models/db/`.
2. Create Pydantic request/response schemas in `app/models/schemas/`.
3. Create a repository in `app/repositories/`.
4. Create a router in `app/api/v1/`.
5. Register the router in `app/api/v1/router.py`.
6. Generate an Alembic migration if new tables are needed.

### Adding a New Template

Templates are data, not code. Create one through the API:

1. `POST /api/v1/templates` with a name and description.
2. `POST /api/v1/templates/{id}/statuses` for each workflow state (set `display_order`, `is_default`, `is_terminal`).
3. `POST /api/v1/templates/{id}/categories` for each task grouping.
4. `POST /api/v1/templates/{id}/categories/{cat_id}/types` for each task type within a category.

Or use the seed script as a reference for doing it programmatically.

---

## Design Decisions

**Why statuses live on Template, not Project** - If statuses were per-project, every new project would need its own status setup. By tying them to the template, teams define their workflow once and every project inherits it. If a specific project eventually needs a custom status set, we can add an override mechanism later.

**Why components live on Project, not Template** - Components are project-specific. The SWIKI project has ETL / API / Frontend, but another project using the same template might have completely different modules.

**Why `assignee` is a string, not an FK** - QC Builder does not own a user directory. Introducing a users table now would mean either duplicating Entra ID data or building a sync mechanism, both of which are premature. A plain string is easy to migrate later when we integrate with a shared user store.

**Why `type_id` is nullable** - Not every task needs sub-classification. Making the field nullable avoids forcing users to pick a type when none fits, which prevents the "Other" anti-pattern.

**Why task history is automatic** - The repository's `update_task()` method diffs the incoming patch against the current row and writes a `task_history` entry for every changed field. This happens at the data access layer so it cannot be bypassed.

---

## Related Services

QC Builder is a standalone project tracking tool, but it sits alongside the broader Internal Knowledge Base ecosystem:

| Directory | Description |
|-----------|-------------|
| `qc-builder` | Angular frontend (QC Builder dashboard) |
| `swiki` | Angular frontend (SWIKI operations portal) |
| `swiki-api` | FastAPI backend for SWIKI |
| `etls` | ETL pipelines for ingesting external data sources |

---

## License

Property of Sphere Entertainment Co. Internal use only. Not for external distribution.