"""Configuration management for the resume parser."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env='OPENAI_API_KEY')
    openai_model: str = Field(default='gpt-4-turbo-preview', env='OPENAI_MODEL')
    openai_max_tokens: int = Field(default=1000, env='OPENAI_MAX_TOKENS')
    openai_temperature: float = Field(default=0.1, env='OPENAI_TEMPERATURE')
    
    # Logging Configuration
    log_level: str = Field(default='INFO', env='LOG_LEVEL')
    log_file: Optional[str] = Field(default=None, env='LOG_FILE')
    
    # Extraction Configuration
    max_skills_returned: int = Field(default=20, env='MAX_SKILLS_RETURNED')
    enable_skill_categorization: bool = Field(default=True, env='ENABLE_SKILL_CATEGORIZATION')
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level is valid."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'log_level must be one of {valid_levels}')
        return v.upper()
    
    @validator('openai_temperature')
    def validate_temperature(cls, v):
        """Validate temperature is in valid range."""
        if not 0 <= v <= 2:
            raise ValueError('openai_temperature must be between 0 and 2')
        return v
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


# Global settings instance
settings = Settings()

