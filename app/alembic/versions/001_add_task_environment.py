"""Add environment column to tasks table

Very first migration

Revision ID: 001_add_task_environment
Revises: <replace-with-current-head>
Create Date: 2026-03-12

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "001_add_task_environment"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column("environment", sa.String(length=10), nullable=True),
    )
    op.create_index("ix_tasks_environment", "tasks", ["environment"])


def downgrade() -> None:
    op.drop_index("ix_tasks_environment", table_name="tasks")
    op.drop_column("tasks", "environment")