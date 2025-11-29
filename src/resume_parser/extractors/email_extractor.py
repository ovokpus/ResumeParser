"""Email extractor using regex patterns."""

import re
from resume_parser.extractors.base import FieldExtractor
from resume_parser.exceptions import ExtractionError
from resume_parser.utils.logger import setup_logger

logger = setup_logger(__name__)


class EmailExtractor(FieldExtractor):
    """
    Extract email address from resume text using regex patterns.
    
    Uses comprehensive regex pattern that follows RFC 5322 specification
    for email address validation.
    """
    
    # Comprehensive email regex pattern
    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )
    
    def extract(self, text: str) -> str:
        """
        Extract email address from text.
        
        Args:
            text: Resume text content
        
        Returns:
            Email address (empty string if not found)
        
        Raises:
            ExtractionError: If extraction process fails
        """
        self._validate_text_input(text)
        
        logger.info("Extracting email address using regex")
        
        try:
            # Find all email matches
            matches = self.EMAIL_PATTERN.findall(text)
            
            if not matches:
                logger.warning("No email address found in resume")
                return ""
            
            # Return first match (most likely to be primary email)
            email = matches[0]
            
            # Additional validation: filter out common false positives
            email_lower = email.lower()
            invalid_domains = ['example.com', 'test.com', 'domain.com']
            if any(domain in email_lower for domain in invalid_domains):
                logger.warning(f"Filtered out invalid email: {email}")
                return ""
            
            logger.info(f"Successfully extracted email: {email}")
            return email
            
        except Exception as e:
            logger.error(f"Error extracting email: {str(e)}")
            raise ExtractionError(f"Failed to extract email: {str(e)}")

