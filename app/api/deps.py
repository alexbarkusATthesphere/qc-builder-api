from collections.abc import Generator

from sqlmodel import Session

from app.db.session import get_session


def get_db() -> Generator[Session, None, None]:
    """Alias for the session dependency. Keeps router imports clean."""
    yield from get_session()