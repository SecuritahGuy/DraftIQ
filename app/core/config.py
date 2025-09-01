"""
Configuration settings for DraftIQ application.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "DraftIQ"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, description="Debug mode")
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./draftiq.db",
        description="Database connection URL"
    )
    
    # Yahoo Fantasy API
    yahoo_client_id: str = Field(default="dev_client_id", description="Yahoo OAuth client ID")
    yahoo_client_secret: str = Field(default="dev_client_secret", description="Yahoo OAuth client secret")
    yahoo_redirect_uri: str = Field(
        default="http://localhost:8000/auth/yahoo/callback",
        description="Yahoo OAuth redirect URI"
    )
    
    # Security
    secret_key: str = Field(default="dev_secret_key_for_development_only_change_in_production", description="Secret key for JWT tokens")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    
    # API
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    
    # Caching
    redis_url: Optional[str] = Field(
        default=None,
        description="Redis URL for caching (optional)"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()
