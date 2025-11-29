"""Configuration management for the resume parser."""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from dotenv import load_dotenv

# Load environment variables from .env file
# Use override=True to prioritize .env file over shell environment variables
load_dotenv(override=True)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(...)
    openai_model: str = Field(default='gpt-4-turbo-preview')
    openai_max_tokens: int = Field(default=1000)
    openai_temperature: float = Field(default=0.1)
    
    # Logging Configuration
    log_level: str = Field(default='INFO')
    log_file: Optional[str] = Field(default=None)
    
    # Extraction Configuration
    max_skills_returned: int = Field(default=20)
    enable_skill_categorization: bool = Field(default=True)
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level is valid."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'log_level must be one of {valid_levels}')
        return v.upper()
    
    @field_validator('openai_temperature')
    @classmethod
    def validate_temperature(cls, v):
        """Validate temperature is in valid range."""
        if not 0 <= v <= 2:
            raise ValueError('openai_temperature must be between 0 and 2')
        return v


# Global settings instance
settings = Settings()

