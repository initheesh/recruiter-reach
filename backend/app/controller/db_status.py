import logging

from fastapi import APIRouter

from app.db import get_db_status, test_database_connection

logger = logging.getLogger(__name__)

router = APIRouter(tags=["db-status"])


@router.get("/db-status")
def get_database_status() -> dict[str, str | bool]:
    is_connected = test_database_connection()
    if not is_connected:
        logger.warning("Database status check failed")
        return {
            "ok": False,
            "status": "unhealthy",
            "detail": "Database is unreachable.",
        }

    # Status helper gives the last known health state tracked by the DB module.
    status_ok = get_db_status()
    return {
        "ok": status_ok,
        "status": "healthy" if status_ok else "unhealthy",
        "detail": "Database connection is available.",
    }
