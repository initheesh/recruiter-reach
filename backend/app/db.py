import logging
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

engine: Engine | None = None
SessionLocal: sessionmaker[Session] | None = None
db_connected = False
Base = declarative_base()


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        logger.warning(
            "DATABASE_URL uses postgresql://; normalizing to postgresql+psycopg://"
        )
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def create_database_engine() -> bool:
    global engine, SessionLocal

    database_url = normalize_database_url(settings.database_url)
    if not database_url:
        logger.error("DATABASE_URL is not configured")
        return False

    try:
        if database_url.startswith("sqlite"):
            engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
            )
        else:
            engine = create_engine(
                database_url,
                connect_args={"sslmode": "require"},
                pool_pre_ping=True,
                pool_recycle=300,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                echo=False,
            )

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("Database engine created successfully")
        return True
    except Exception:
        logger.exception("Failed to create database engine")
        engine = None
        SessionLocal = None
        return False


def test_database_connection() -> bool:
    global db_connected

    if engine is None and not create_database_engine():
        db_connected = False
        return False

    if engine is None:
        db_connected = False
        return False

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_connected = True
        return True
    except SQLAlchemyError:
        db_connected = False
        logger.exception("Database connection test failed")
        return False
    except Exception:
        db_connected = False
        logger.exception("Unexpected error during database connection test")
        return False


def get_db_status() -> bool:
    return db_connected


def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None and not create_database_engine():
        raise RuntimeError("Database engine is not initialized")

    if SessionLocal is None:
        raise RuntimeError("Database session factory is not available")

    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError:
        db.rollback()
        raise
    finally:
        db.close()


def safe_get_db() -> Session | None:
    if SessionLocal is None and not create_database_engine():
        return None

    if SessionLocal is None:
        return None

    try:
        return SessionLocal()
    except Exception:
        logger.exception("Could not create a database session")
        return None


create_database_engine()
