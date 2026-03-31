from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Wealth OS"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql://wealthos:wealthos_secret@localhost:5432/wealthos"

    # Auth
    SECRET_KEY: str = "change_me_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # Uploads
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50

    # Market data providers (fill in via .env when ready)
    SAUDI_MARKET_API_KEY: str = ""
    SAUDI_MARKET_BASE_URL: str = ""
    US_MARKET_API_KEY: str = ""
    US_MARKET_BASE_URL: str = ""
    FX_PROVIDER_API_KEY: str = ""
    FX_PROVIDER_BASE_URL: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
