"""Name extractor using rule-based approach and NER."""

import re
import spacy
from typing import Optional
from resume_parser.extractors.base import FieldExtractor
from resume_parser.exceptions import ExtractionError
from resume_parser.utils.logger import setup_logger

logger = setup_logger(__name__)


class NameExtractor(FieldExtractor):
    """
    Extract candidate name using combined rule-based and NER approach.
    
    Strategy:
    1. First, try to extract name from top of resume (heuristic)
    2. If unsuccessful, use SpaCy NER to identify PERSON entities
    3. Apply validation rules to ensure extracted name is reasonable
    """
    
    def __init__(self):
        """Initialize SpaCy NER model."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded SpaCy model for name extraction")
        except OSError:
            logger.error(
                "SpaCy model 'en_core_web_sm' not found. "
                "Run: python -m spacy download en_core_web_sm"
            )
            raise ExtractionError(
                "SpaCy model not available. Please install with: "
                "python -m spacy download en_core_web_sm"
            )
    
    def extract(self, text: str) -> str:
        """
        Extract candidate name from resume text.
        
        Args:
            text: Resume text content
        
        Returns:
            Candidate name (empty string if not found)
        
        Raises:
            ExtractionError: If extraction process fails
        """
        self._validate_text_input(text)
        
        logger.info("Extracting name using rule-based + NER approach")
        
        try:
            # Strategy 1: Extract from top of resume (first 500 chars)
            name = self._extract_name_from_header(text[:500])
            if name:
                logger.info(f"Extracted name from header: {name}")
                return name
            
            # Strategy 2: Use SpaCy NER on full text
            name = self._extract_name_with_ner(text)
            if name:
                logger.info(f"Extracted name using NER: {name}")
                return name
            
            logger.warning("No valid name found in resume")
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting name: {str(e)}")
            raise ExtractionError(f"Failed to extract name: {str(e)}")
    
    def _extract_name_from_header(self, header_text: str) -> Optional[str]:
        """
        Extract name from resume header using heuristics.
        
        Resumes typically have the candidate's name prominently at the top,
        often in the first 1-3 lines.
        
        Args:
            header_text: First portion of resume text
        
        Returns:
            Extracted name or None
        """
        lines = header_text.split('\n')
        
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip lines that look like contact info or addresses
            if any(keyword in line.lower() for keyword in [
                'email', 'phone', 'address', 'linkedin', 'github', 'http', '@'
            ]):
                continue
            
            # Check if line looks like a name
            if self._is_valid_name(line):
                return line
        
        return None
    
    def _extract_name_with_ner(self, text: str) -> Optional[str]:
        """
        Extract name using SpaCy Named Entity Recognition.
        
        Args:
            text: Full resume text
        
        Returns:
            Extracted name or None
        """
        # Process text with SpaCy (limit to first 1000 chars for efficiency)
        doc = self.nlp(text[:1000])
        
        # Find all PERSON entities
        person_entities = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        
        if not person_entities:
            return None
        
        # Return first valid person entity
        for entity in person_entities:
            if self._is_valid_name(entity):
                return entity
        
        return None
    
    def _is_valid_name(self, text: str) -> bool:
        """
        Validate that text looks like a name.
        
        Rules:
        - Contains 2-5 words (e.g., "John Doe" or "Mary Jane Smith")
        - Each word is 2-20 characters
        - Contains only letters, spaces, hyphens, apostrophes
        - Starts with capital letter
        
        Args:
            text: Text to validate
        
        Returns:
            True if text looks like a valid name
        """
        # Must not be empty
        if not text or not text.strip():
            return False
        
        # Clean and check pattern
        text = text.strip()
        
        # Must start with capital letter
        if not text[0].isupper():
            return False
        
        # Check character composition
        if not re.match(r"^[A-Za-z\s\-'\.]+$", text):
            return False
        
        # Split into words
        words = text.split()
        
        # Must have 2-5 words
        if not 2 <= len(words) <= 5:
            return False
        
        # Each word must be reasonable length
        for word in words:
            if not 2 <= len(word) <= 20:
                return False
        
        return True

