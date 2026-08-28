"""Tests for database engine and connection checking."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.db.session import check_database_connection, create_db_engine


def test_sqlite_engine_creation() -> None:
    """Verify SQLite engine creates properly."""
    engine = create_db_engine("sqlite:///:memory:")
    assert engine is not None


def test_check_database_connection_with_live_session(db_session: Session) -> None:
    """Verify check_database_connection returns connected for active session."""
    is_ok, msg = check_database_connection(db_session)
    assert is_ok is True
    assert msg == "connected"
