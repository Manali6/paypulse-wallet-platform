"""Wallet Platform — FastAPI Application Factory."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.limiter import limiter
from app.metrics import HTTP_ERRORS_TOTAL
from app.routers import auth, fx, health, transactions, transfers, users, wallets

settings = get_settings()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── CORS Middleware (Outermost middleware) ──
    application.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Middleware for Tracking 4xx/5xx Errors in Prometheus ──
    @application.middleware("http")
    async def track_error_metrics(request: Request, call_next):
        try:
            response = await call_next(request)
            if response.status_code >= 400:
                HTTP_ERRORS_TOTAL.labels(
                    status_code=str(response.status_code),
                    method=request.method,
                    path=request.url.path,
                ).inc()
            return response
        except Exception:
            HTTP_ERRORS_TOTAL.labels(
                status_code="500",
                method=request.method,
                path=request.url.path,
            ).inc()
            raise

    # ── Prometheus Instrumentator ─────────────────────────
    Instrumentator().instrument(application).expose(application, endpoint="/metrics")

    # ── Routers ───────────────────────────────────────────
    application.include_router(health.router)
    application.include_router(auth.router)
    application.include_router(users.router)
    application.include_router(wallets.router)
    application.include_router(transfers.router)
    application.include_router(fx.router)
    application.include_router(transactions.router)

    return application


app = create_app()
