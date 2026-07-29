"""Health check router — liveness and readiness checks for database, Redis, and migrations."""

import redis
from fastapi import APIRouter
from sqlalchemy import text

from app.config import get_settings
from app.database import SessionLocal

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health")
def health_check():
    """Health check endpoint — probes database, Redis, and version metadata."""
    checks = {}
    overall_status = "healthy"

    # Check database
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        # Get latest applied migration version
        alembic_ver = db.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar()
        db.close()
        checks["database"] = {
            "status": "healthy",
            "migration_version": alembic_ver or "unknown",
        }
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "unhealthy"

    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL, socket_timeout=2.0)
        r.ping()
        checks["redis"] = {"status": "healthy"}
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "error": str(e)}
        if overall_status != "unhealthy":
            overall_status = "degraded"

    return {
        "status": overall_status,
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "checks": checks,
    }
