"""
Application configuration using Pydantic Settings.

This module provides centralized configuration management with validation.
All environment variables are defined here with their defaults and descriptions.
"""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    # LLM Configuration
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    OLLAMA_MODEL: str = "llama2"
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Vector Database Configuration
    VECTOR_DB_PATH: str = "./vector_db"
    
    # RAG Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 7
    LLM_TEMPERATURE: float = 0.7

    # Database configuration (PostgreSQL)
    DATABASE_URL: str = (
        "postgresql+psycopg2://rag_user:rag_password@localhost:5432/rag_chat"
    )

    # Auth / JWT
    JWT_SECRET_KEY: str = "CHANGE_ME_SUPER_SECRET_KEY"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 240
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = False
    
    # CORS Configuration
    CORS_ORIGINS: str = "*"

    # AWS / S3 configuration (values come from environment)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"

    S3_BUCKET_NAME: Optional[str] = None
    S3_PREFIX: str = "uploads/"


settings = Settings()
