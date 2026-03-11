from sqlmodel import SQLModel, create_engine

from app.core.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args=connect_args,
)


def init_db() -> None:
    """Create all tables that don't exist yet.

    Called once on app startup via the lifespan handler. Import all
    ORM models before calling this so SQLModel registers them.
    """
    SQLModel.metadata.create_all(engine)