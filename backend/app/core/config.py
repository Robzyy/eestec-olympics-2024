from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Essay Analysis API"
    DEBUG: bool = False
    
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_KEY: str
    AZURE_OPENAI_DEPLOYMENT_NAME: str
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    
    # Azure Language Service
    AZURE_LANGUAGE_ENDPOINT: str
    AZURE_LANGUAGE_KEY: str
    
    # Azure Document Intelligence
    AZURE_DOCUMENT_ENDPOINT: str
    AZURE_DOCUMENT_KEY: str
    
    # Azure Computer Vision
    AZURE_VISION_ENDPOINT: str
    AZURE_VISION_KEY: str
    
    SECRET_KEY: str  # Will be loaded from environment variable
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database Settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# You can keep this for backward compatibility
settings = get_settings()
