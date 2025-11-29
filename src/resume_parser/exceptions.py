"""Custom exceptions for the resume parser framework."""


class ResumeParserError(Exception):
    """Base exception for all resume parser errors."""
    pass


class FileParsingError(ResumeParserError):
    """Raised when file parsing fails."""
    pass


class ExtractionError(ResumeParserError):
    """Raised when field extraction fails."""
    pass


class ValidationError(ResumeParserError):
    """Raised when input validation fails."""
    pass


class ConfigurationError(ResumeParserError):
    """Raised when configuration is invalid."""
    pass


class APIError(ResumeParserError):
    """Raised when external API calls fail."""
    pass

