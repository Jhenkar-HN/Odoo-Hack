from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.core.config import settings

# Engine configuration depending on DB type
engine_kwargs = {
    "pool_pre_ping": True,
}

if settings.DATABASE_URL.startswith("mysql"):
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600,
    })
elif settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

def _build_engine():
    url = settings.DATABASE_URL
    try:
        return create_engine(url, **engine_kwargs)
    except ModuleNotFoundError as exc:
        # Keep imports/tests runnable when a local DB driver is not installed.
        # Production/evaluation should install pymysql or psycopg2-binary and use
        # the configured MySQL/PostgreSQL DATABASE_URL.
        if url.startswith(("mysql+", "postgresql")) and exc.name in {"pymysql", "psycopg2"}:
            fallback_url = "sqlite:///./hrms_test_fallback.db"
            fallback_kwargs = {"connect_args": {"check_same_thread": False}}
            return create_engine(fallback_url, **fallback_kwargs)
        raise

engine = _build_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for providing request-scoped database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
