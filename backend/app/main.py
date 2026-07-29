"""Wallet Platform — FastAPI Application Factory."""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings
from app.routers import auth, wallets, transactions, health
from app.middleware.metrics import http_errors_total
from app.exceptions import WalletPlatformError

settings = get_settings()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── Routers ───────────────────────────────────────────
    application.include_router(health.router)
    application.include_router(auth.router)
    application.include_router(wallets.router)
    application.include_router(transactions.router)

    # ── CORS (Added last so it's the outermost middleware) ──
    application.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return application


app = create_app()
