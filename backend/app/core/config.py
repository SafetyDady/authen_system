"""
Core configuration settings for the Authentication System.
"""

import os
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application
    APP_NAME: str = "Authentication System API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Enterprise Authentication System with Role-based Access Control"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    RELOAD: bool = Field(default=True, env="RELOAD")
    
    # Security
    SECRET_KEY: str = Field(env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Database
    DATABASE_URL: str = Field(env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="BACKEND_CORS_ORIGINS"
    )
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Email Configuration
    SMTP_TLS: bool = Field(default=True, env="SMTP_TLS")
    SMTP_PORT: Optional[int] = Field(default=587, env="SMTP_PORT")
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    EMAILS_FROM_EMAIL: Optional[EmailStr] = Field(default=None, env="EMAILS_FROM_EMAIL")
    EMAILS_FROM_NAME: Optional[str] = Field(default=None, env="EMAILS_FROM_NAME")
    
    # File Upload
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=["image/jpeg", "image/png", "image/gif", "application/pdf"],
        env="ALLOWED_FILE_TYPES"
    )
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    # Admin User (for initial setup)
    FIRST_SUPERUSER_EMAIL: EmailStr = Field(env="FIRST_SUPERUSER_EMAIL")
    FIRST_SUPERUSER_PASSWORD: str = Field(env="FIRST_SUPERUSER_PASSWORD")
    
    # Role Configuration
    DEFAULT_USER_ROLE: str = Field(default="user", env="DEFAULT_USER_ROLE")
    AVAILABLE_ROLES: List[str] = Field(
        default=["superadmin", "admin1", "admin2", "admin3", "user"],
        env="AVAILABLE_ROLES"
    )
    
    # Session Configuration
    SESSION_COOKIE_NAME: str = Field(default="auth_session", env="SESSION_COOKIE_NAME")
    SESSION_COOKIE_SECURE: bool = Field(default=True, env="SESSION_COOKIE_SECURE")
    SESSION_COOKIE_HTTPONLY: bool = Field(default=True, env="SESSION_COOKIE_HTTPONLY")
    SESSION_COOKIE_SAMESITE: str = Field(default="lax", env="SESSION_COOKIE_SAMESITE")
    
    # Password Policy
    PASSWORD_MIN_LENGTH: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(default=True, env="PASSWORD_REQUIRE_UPPERCASE")
    PASSWORD_REQUIRE_LOWERCASE: bool = Field(default=True, env="PASSWORD_REQUIRE_LOWERCASE")
    PASSWORD_REQUIRE_NUMBERS: bool = Field(default=True, env="PASSWORD_REQUIRE_NUMBERS")
    PASSWORD_REQUIRE_SPECIAL: bool = Field(default=True, env="PASSWORD_REQUIRE_SPECIAL")
    
    # Account Lockout
    MAX_LOGIN_ATTEMPTS: int = Field(default=5, env="MAX_LOGIN_ATTEMPTS")
    LOCKOUT_DURATION_MINUTES: int = Field(default=30, env="LOCKOUT_DURATION_MINUTES")
    
    # Audit Logging
    AUDIT_LOG_ENABLED: bool = Field(default=True, env="AUDIT_LOG_ENABLED")
    AUDIT_LOG_RETENTION_DAYS: int = Field(default=90, env="AUDIT_LOG_RETENTION_DAYS")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


class DevelopmentSettings(Settings):
    """Development environment settings."""
    DEBUG: bool = True
    RELOAD: bool = True
    LOG_LEVEL: str = "DEBUG"


class ProductionSettings(Settings):
    """Production environment settings."""
    DEBUG: bool = False
    RELOAD: bool = False
    LOG_LEVEL: str = "INFO"
    SESSION_COOKIE_SECURE: bool = True


class TestingSettings(Settings):
    """Testing environment settings."""
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "test-secret-key-not-for-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    FIRST_SUPERUSER_EMAIL: EmailStr = "test@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "testpassword123"


def get_settings() -> Settings:
    """Get settings based on environment."""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Global settings instance
settings = get_settings()

