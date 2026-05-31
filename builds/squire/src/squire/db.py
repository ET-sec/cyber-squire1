"""SQLAlchemy engine + session for the Squire Postgres database (name from CD_DB_NAME)."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .settings import get_settings


_engine: Engine | None = None
_session_factory: sessionmaker | None = None


def _build_dsn() -> str:
    s = get_settings()
    user = quote_plus(s.cd_db_user)
    pwd = quote_plus(s.cd_db_pass.get_secret_value())
    host = s.cd_db_host
    port = s.cd_db_port
    name = s.cd_db_name
    return f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{name}"


def get_engine() -> Engine:
    global _engine, _session_factory
    if _engine is None:
        _engine = create_engine(_build_dsn(), pool_pre_ping=True, pool_size=5, max_overflow=5)
        _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


@contextmanager
def session_scope() -> Iterator[Session]:
    get_engine()
    assert _session_factory is not None
    s = _session_factory()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


def ping() -> bool:
    """Return True if a trivial SELECT 1 succeeds."""
    try:
        eng = get_engine()
        with eng.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        return True
    except Exception:
        return False
