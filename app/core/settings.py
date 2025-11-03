"""Core configuration and settings for the travel planning application."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./travel_db.sqlite",
        env="DATABASE_URL"
    )
    
    # API Keys
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    rapidapi_key: Optional[str] = Field(default=None, env="RAPIDAPI_KEY")
    opentripmap_api_key: Optional[str] = Field(default=None, env="OPENTRIPMAP_API_KEY")
    serpapi_key: Optional[str] = Field(default=None, env="SERPAPI_KEY")
    
    # Google OAuth
    google_oauth_client_id: Optional[str] = Field(default=None, env="GOOGLE_OAUTH_CLIENT_ID")
    google_oauth_client_secret: Optional[str] = Field(default=None, env="GOOGLE_OAUTH_CLIENT_SECRET")
    
    # Application
    app_name: str = Field(default="Travel Planning API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    base_url: str = Field(default="http://localhost:8001", env="BASE_URL")
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-change-this-in-production",
        env="SECRET_KEY"
    )
    access_token_expire_days: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_DAYS")
    
    # External APIs
    google_flights_base_url: str = "https://www.googleapis.com/travel/v1"
    google_maps_base_url: str = "https://maps.googleapis.com/maps/api/v1"


    @property
    def OPENAI_API_KEY(self) -> Optional[str]:
        """Get OpenAI API key."""
        return self.openai_api_key
    
    @property 
    def SERPAPI_KEY(self) -> Optional[str]:
        """Get SerpApi key."""
        return self.serpapi_key

# Global settings instance
settings = Settings()