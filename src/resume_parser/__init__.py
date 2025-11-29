"""Resume Parser Framework - A production-ready resume parsing solution."""

from resume_parser.core.framework import ResumeParserFramework
from resume_parser.models import ResumeData
from resume_parser.exceptions import (
    ResumeParserError,
    FileParsingError,
    ExtractionError,
    ValidationError,
    ConfigurationError,
    APIError
)

__version__ = "1.0.0"
__all__ = [
    "ResumeParserFramework",
    "ResumeData",
    "ResumeParserError",
    "FileParsingError",
    "ExtractionError",
    "ValidationError",
    "ConfigurationError",
    "APIError",
]

