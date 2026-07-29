from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://wallet:wallet_secret@localhost:5432/wallet_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "dev-jwt-secret-change-in-production"
    JWT_REFRESH_SECRET: str = "dev-jwt-refresh-secret-change-in-production"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://localhost:3000,http://localhost:3002"
    )

    # App
    ENVIRONMENT: str = "development"
    APP_NAME: str = "Wallet Platform"
    APP_VERSION: str = "1.0.0"

    # File uploads
    MAX_UPLOAD_SIZE_MB: int = 5

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
