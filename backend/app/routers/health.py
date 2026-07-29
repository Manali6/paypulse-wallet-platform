"""Health check router — liveness and readiness checks."""

from fastapi import APIRouter
from sqlalchemy import text

from app.config import get_settings
from app.database import SessionLocal

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health")
def health_check():
    """Health check endpoint — verifies database and Redis connectivity."""
    checks = {}
    overall_status = "healthy"

    # Check database
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        checks["database"] = {"status": "healthy"}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "unhealthy"

    # Check Redis
    try:
        import redis

        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        checks["redis"] = {"status": "healthy"}
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "error": str(e)}
        if overall_status != "unhealthy":
            overall_status = "degraded"

    return {
        "status": overall_status,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": checks,
    }
