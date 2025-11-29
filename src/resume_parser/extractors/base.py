"""Abstract base class for field extractors."""

from abc import ABC, abstractmethod
from typing import Any
from resume_parser.utils.logger import setup_logger

logger = setup_logger(__name__)


class FieldExtractor(ABC):
    """
    Abstract base class for extracting specific fields from resume text.
    
    Each concrete implementation extracts one field (name, email, or skills)
    using an appropriate strategy (regex, NER, LLM, etc.).
    """
    
    @abstractmethod
    def extract(self, text: str) -> Any:
        """
        Extract a specific field from resume text.
        
        Args:
            text: Raw text content from parsed resume
        
        Returns:
            Extracted field value (type depends on field)
        
        Raises:
            ExtractionError: If extraction fails
        """
        pass
    
    def _validate_text_input(self, text: str) -> None:
        """
        Validate that input text is not empty.
        
        Args:
            text: Text to validate
        
        Raises:
            ValueError: If text is empty
        """
        if not text or not text.strip():
            raise ValueError("Cannot extract from empty text")

