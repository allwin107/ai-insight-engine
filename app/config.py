"""
Configuration Management
Loads settings from environment variables
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_URL: str = "http://localhost:8000"
    CORS_ORIGINS: List[str] = ["http://localhost:8501", "http://localhost:3000"]
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:8501"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440  # 24 hours
    
    # LLM
    LLM_ENDPOINT: str = ""
    LLM_TIMEOUT: int = 60
    LLM_MAX_RETRIES: int = 3
    LLM_MODEL: str = "llama3.1:8b-instruct-q4_0"
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    MAX_ROWS: int = 10000
    ALLOWED_EXTENSIONS: str = "csv,xlsx,xls"  # Changed to string, will parse in property
    UPLOAD_DIR: str = "/tmp/uploads"
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse ALLOWED_EXTENSIONS string into list"""
        if isinstance(self.ALLOWED_EXTENSIONS, str):
            return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(',')]
        return self.ALLOWED_EXTENSIONS
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 10
    RATE_LIMIT_WINDOW: int = 3600
    
    # Cleanup
    CLEANUP_AFTER_MINUTES: int = 5
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Monitoring (Optional)
    SENTRY_DSN: str = ""
    POSTHOG_API_KEY: str = ""
    POSTHOG_HOST: str = "https://app.posthog.com"
    
    # Email (Optional)
    SENDGRID_API_KEY: str = ""
    FROM_EMAIL: str = ""

# Create global settings instance
settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)