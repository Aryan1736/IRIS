"""Database engine and session management."""

from __future__ import annotations

import logging
from collections.abc import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import settings

LOGGER = logging.getLogger("paimana.db.session")


def create_db_engine(database_url: str) -> Engine:
    """Create a SQLAlchemy engine configured for PostgreSQL or SQLite."""
    if database_url.startswith("sqlite"):
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG and settings.ENVIRONMENT == "development",
        )
    return create_engine(
        database_url,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        echo=settings.DEBUG and settings.ENVIRONMENT == "development",
    )


engine: Engine = create_db_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session and closes it on exit."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection(session: Session | None = None) -> tuple[bool, str]:
    """Execute a simple query (SELECT 1) to verify database connectivity."""
    try:
        if session is not None:
            session.execute(text("SELECT 1"))
        else:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        return True, "connected"
    except Exception as exc:
        LOGGER.warning("Database connectivity check failed: %s", str(exc))
        return False, str(exc)
