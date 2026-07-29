"""Wallet Platform — FastAPI Application Factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
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

    # ── Routers ───────────────────────────────────────────
    application.include_router(health.router)
    application.include_router(auth.router)
    application.include_router(users.router)
    application.include_router(wallets.router)
    application.include_router(transfers.router)
    application.include_router(fx.router)
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
