"""Abstract base class for file parsers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union
from resume_parser.utils.logger import setup_logger

logger = setup_logger(__name__)


class FileParser(ABC):
    """
    Abstract base class for parsing resume files.
    
    Implementations must extract raw text from different file formats
    (PDF, DOCX, etc.) and return it as a string for downstream processing.
    """
    
    @abstractmethod
    def parse(self, file_path: Union[str, Path]) -> str:
        """
        Extract text content from a file.
        
        Args:
            file_path: Path to the resume file
        
        Returns:
            Extracted text content as a string
        
        Raises:
            FileParsingError: If file cannot be parsed
            FileNotFoundError: If file doesn't exist
            ValidationError: If file format is invalid
        """
        pass
    
    def _validate_file_exists(self, file_path: Union[str, Path]) -> Path:
        """
        Validate that file exists and return Path object.
        
        Args:
            file_path: Path to validate
        
        Returns:
            Path object
        
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        if not path.is_file():
            logger.error(f"Path is not a file: {file_path}")
            raise ValueError(f"Path is not a file: {file_path}")
        return path
    
    def _validate_file_size(self, file_path: Path, max_size_mb: int = 10) -> None:
        """
        Validate file size is within acceptable limits.
        
        Args:
            file_path: Path to file
            max_size_mb: Maximum file size in megabytes
        
        Raises:
            ValidationError: If file is too large
        """
        from resume_parser.exceptions import ValidationError
        
        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ValidationError(
                f"File size ({size_mb:.2f}MB) exceeds maximum ({max_size_mb}MB)"
            )

