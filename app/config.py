import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    APP_NAME: str = "StreamPicker"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./streampicker.db"
    
    # Redis Cache & Rate Limiting
    REDIS_URL: Optional[str] = None
    
    # TMDB API
    TMDB_API_KEY: Optional[str] = None
    TMDB_READ_ACCESS_TOKEN: Optional[str] = None
    TMDB_DEFAULT_REGION: str = "IN"
    
    # Watchmode API
    WATCHMODE_API_KEY: Optional[str] = None
    
    # Default User
    DEFAULT_USER_ID: str = "default_user"
    
    # Cache & Rate limits
    CACHE_DEFAULT_TTL: int = 300
    RATE_LIMIT_RPM: int = 180
    RATE_LIMIT_BURST: int = 60

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str]) -> str:
        if isinstance(v, str):
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql://", 1)
        return v or "sqlite:///./streampicker.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
