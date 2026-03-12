"""Alembic environment configuration.

This file is the bridge between Alembic and your application. It:
  1. Reads the DATABASE_URL from app.core.config (which reads from .env)
  2. Imports all SQLModel ORM models so metadata knows about every table
  3. Provides that metadata to Alembic for autogenerate support

Usage from the project root:
    alembic upgrade head          # Apply all pending migrations
    alembic downgrade -1          # Roll back the last migration
    alembic current               # Show which revision the DB is at
    alembic history               # Show the migration chain
    alembic revision --autogenerate -m "describe the change"
                                  # Auto-detect model changes and create a script
"""

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# ---------------------------------------------------------------------------
# Make sure the project root is on sys.path so 'app.*' imports work
# when Alembic is invoked from the project root directory.
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# ---------------------------------------------------------------------------
# Import application config (pulls DATABASE_URL from .env)
# ---------------------------------------------------------------------------
from app.core.config import settings  # noqa: E402

# ---------------------------------------------------------------------------
# Import ALL ORM models so SQLModel.metadata registers every table.
# Without these imports, autogenerate won't see your tables.
# ---------------------------------------------------------------------------
from app.models.db.project import Project, ProjectComponent  # noqa: E402, F401
from app.models.db.task import Task, TaskComment, TaskHistory  # noqa: E402, F401
from app.models.db.template import (  # noqa: E402, F401
    StatusDefinition,
    TaskCategory,
    TaskType,
    Template,
)

# ---------------------------------------------------------------------------
# Alembic Config object — gives access to values in alembic.ini
# ---------------------------------------------------------------------------
config = context.config

# Set the database URL from your app settings so alembic.ini doesn't
# need to hard-code it (and .env overrides work automatically).
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Configure Python logging from the [loggers] section of alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The metadata object that Alembic uses for autogenerate.
# Because we imported all models above, this already has every table.
target_metadata = SQLModel.metadata


# ---------------------------------------------------------------------------
# Offline mode — generates SQL scripts without a live DB connection.
# Useful for review or running in environments without direct DB access.
#   alembic upgrade head --sql
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online mode — connects to the database and applies migrations directly.
# This is what runs when you do: alembic upgrade head
# ---------------------------------------------------------------------------
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    # For SQLite, we need check_same_thread=False just like your engine
    connect_args = {}
    url = config.get_main_option("sqlalchemy.url")
    if url and url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()