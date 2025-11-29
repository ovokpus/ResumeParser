"""Coordinator for orchestrating field extraction."""

from typing import Dict, Type
from resume_parser.models import ResumeData
from resume_parser.extractors.base import FieldExtractor
from resume_parser.extractors.name_extractor import NameExtractor
from resume_parser.extractors.email_extractor import EmailExtractor
from resume_parser.extractors.skills_extractor import SkillsExtractor
from resume_parser.exceptions import ExtractionError
from resume_parser.utils.logger import setup_logger

logger = setup_logger(__name__)


class ResumeExtractor:
    """
    Coordinate the extraction of all fields from resume text.
    
    Orchestrates multiple FieldExtractor instances to extract
    name, email, and skills, then combines results into ResumeData.
    
    Uses Strategy pattern: different extractors for different fields.
    """
    
    def __init__(
        self,
        name_extractor: FieldExtractor = None,
        email_extractor: FieldExtractor = None,
        skills_extractor: FieldExtractor = None
    ):
        """
        Initialize with field extractors (dependency injection).
        
        Args:
            name_extractor: Extractor for name field (default: NameExtractor)
            email_extractor: Extractor for email field (default: EmailExtractor)
            skills_extractor: Extractor for skills field (default: SkillsExtractor)
        """
        self.name_extractor = name_extractor or NameExtractor()
        self.email_extractor = email_extractor or EmailExtractor()
        self.skills_extractor = skills_extractor or SkillsExtractor()
        
        logger.info("Initialized ResumeExtractor with all field extractors")
    
    def extract(self, text: str) -> ResumeData:
        """
        Extract all fields from resume text.
        
        Attempts to extract all fields even if some fail, providing
        partial results with empty strings/lists for failed extractions.
        
        Args:
            text: Parsed resume text content
        
        Returns:
            ResumeData object with extracted fields
        
        Raises:
            ExtractionError: If extraction process fails critically
        """
        if not text or not text.strip():
            raise ExtractionError("Cannot extract from empty text")
        
        logger.info("Beginning field extraction from resume text")
        
        # Track extraction results and errors
        results = {
            "name": "",
            "email": "",
            "skills": []
        }
        errors = {}
        
        # Extract name
        try:
            results["name"] = self.name_extractor.extract(text)
            logger.info(f"Name extraction: {'success' if results['name'] else 'no result'}")
        except Exception as e:
            logger.error(f"Name extraction failed: {str(e)}")
            errors["name"] = str(e)
        
        # Extract email
        try:
            results["email"] = self.email_extractor.extract(text)
            logger.info(f"Email extraction: {'success' if results['email'] else 'no result'}")
        except Exception as e:
            logger.error(f"Email extraction failed: {str(e)}")
            errors["email"] = str(e)
        
        # Extract skills
        try:
            results["skills"] = self.skills_extractor.extract(text)
            logger.info(
                f"Skills extraction: {'success' if results['skills'] else 'no result'} "
                f"({len(results['skills'])} skills)"
            )
        except Exception as e:
            logger.error(f"Skills extraction failed: {str(e)}")
            errors["skills"] = str(e)
        
        # Log warning if all extractions failed
        if all(not v or v == [] for v in results.values()):
            logger.warning(
                "All field extractions failed or returned empty results. "
                f"Errors: {errors}"
            )
        
        # Create ResumeData (dataclass handles normalization in __post_init__)
        resume_data = ResumeData(
            name=results["name"],
            email=results["email"],
            skills=results["skills"]
        )
        
        logger.info(
            f"Extraction complete - Name: {bool(resume_data.name)}, "
            f"Email: {bool(resume_data.email)}, "
            f"Skills: {len(resume_data.skills)}"
        )
        
        return resume_data

