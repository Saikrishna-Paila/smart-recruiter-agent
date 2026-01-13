"""
Settings Configuration
======================

Centralized settings management using Pydantic.
All settings loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ==========================================================================
    # Application
    # ==========================================================================
    app_name: str = Field(default="Smart Recruiter")
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)
    secret_key: str = Field(default="change-me-in-production")

    # ==========================================================================
    # API Settings
    # ==========================================================================
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    frontend_url: str = Field(default="http://localhost:5173")

    # ==========================================================================
    # Groq LLM (FREE!)
    # ==========================================================================
    groq_api_key: str = Field(default="", env="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile")

    # ==========================================================================
    # Qdrant Vector Database
    # ==========================================================================
    qdrant_url: str = Field(default="", env="QDRANT_URL")
    qdrant_api_key: str = Field(default="", env="QDRANT_API_KEY")
    qdrant_collection: str = Field(default="smart_recruiter")

    # ==========================================================================
    # Database
    # ==========================================================================
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/smart_recruiter.db"
    )

    # ==========================================================================
    # Email (Optional)
    # ==========================================================================
    resend_api_key: Optional[str] = Field(default=None, env="RESEND_API_KEY")
    email_from: str = Field(default="recruiter@example.com")

    # ==========================================================================
    # File Storage
    # ==========================================================================
    upload_dir: str = Field(default="./data/uploads")
    resume_dir: str = Field(default="./data/resumes")
    max_file_size_mb: int = Field(default=10)

    # ==========================================================================
    # CrewAI Settings
    # ==========================================================================
    crew_verbose: bool = Field(default=True)
    crew_memory: bool = Field(default=True)

    # ==========================================================================
    # Scoring Weights
    # ==========================================================================
    weight_skills: float = Field(default=0.4)
    weight_experience: float = Field(default=0.3)
    weight_education: float = Field(default=0.2)
    weight_culture: float = Field(default=0.1)
    min_match_score: int = Field(default=60)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def weights(self) -> dict:
        return {
            "skills": self.weight_skills,
            "experience": self.weight_experience,
            "education": self.weight_education,
            "culture": self.weight_culture,
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance for convenience
settings = get_settings()
