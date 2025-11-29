"""Main framework class - public API."""

from pathlib import Path
from typing import Union, Dict, Type
from resume_parser.models import ResumeData
from resume_parser.parsers.base import FileParser
from resume_parser.parsers.pdf_parser import PDFParser
from resume_parser.parsers.word_parser import WordParser
from resume_parser.core.resume_extractor import ResumeExtractor
from resume_parser.exceptions import ResumeParserError, ValidationError
from resume_parser.utils.logger import setup_logger

logger = setup_logger(__name__)


class ResumeParserFramework:
    """
    Main framework for parsing resumes.
    
    This is the primary public API. Users interact with this class
    to parse resumes from various file formats.
    
    Example:
        >>> framework = ResumeParserFramework()
        >>> resume_data = framework.parse_resume("path/to/resume.pdf")
        >>> print(resume_data.to_dict())
    """
    
    # Map file extensions to parser classes
    PARSER_REGISTRY: Dict[str, Type[FileParser]] = {
        ".pdf": PDFParser,
        ".docx": WordParser,
    }
    
    def __init__(self, resume_extractor: ResumeExtractor = None):
        """
        Initialize the framework.
        
        Args:
            resume_extractor: Custom ResumeExtractor (default: creates new instance)
        """
        self.resume_extractor = resume_extractor or ResumeExtractor()
        logger.info("Initialized ResumeParserFramework")
    
    def parse_resume(self, file_path: Union[str, Path]) -> ResumeData:
        """
        Parse a resume file and extract structured data.
        
        This is the main entry point for the framework.
        
        Args:
            file_path: Path to resume file (.pdf or .docx)
        
        Returns:
            ResumeData object containing extracted fields
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValidationError: If file format is not supported
            FileParsingError: If file cannot be parsed
            ExtractionError: If field extraction fails
            ResumeParserError: For other errors
        """
        logger.info(f"=" * 60)
        logger.info(f"Starting resume parsing: {file_path}")
        logger.info(f"=" * 60)
        
        try:
            # Convert to Path object
            path = Path(file_path)
            
            # Validate file exists
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Get file extension
            extension = path.suffix.lower()
            
            # Get appropriate parser
            parser_class = self.PARSER_REGISTRY.get(extension)
            if not parser_class:
                supported = ", ".join(self.PARSER_REGISTRY.keys())
                raise ValidationError(
                    f"Unsupported file format: {extension}. "
                    f"Supported formats: {supported}"
                )
            
            logger.info(f"Using parser: {parser_class.__name__}")
            
            # Parse file to extract text
            parser = parser_class()
            text = parser.parse(path)
            
            logger.info(f"Extracted {len(text)} characters of text")
            
            # Extract fields from text
            resume_data = self.resume_extractor.extract(text)
            
            logger.info("=" * 60)
            logger.info("Resume parsing completed successfully")
            logger.info(f"Results: {resume_data.to_dict()}")
            logger.info("=" * 60)
            
            return resume_data
            
        except (FileNotFoundError, ValidationError) as e:
            # Re-raise validation errors as-is
            logger.error(f"Validation error: {str(e)}")
            raise
        
        except ResumeParserError as e:
            # Re-raise known framework errors
            logger.error(f"Parsing error: {str(e)}")
            raise
        
        except Exception as e:
            # Wrap unexpected errors
            logger.error(f"Unexpected error parsing resume: {str(e)}", exc_info=True)
            raise ResumeParserError(f"Unexpected error: {str(e)}")
    
    @classmethod
    def register_parser(cls, extension: str, parser_class: Type[FileParser]) -> None:
        """
        Register a new file parser for a specific extension.
        
        This allows extending the framework with custom parsers.
        
        Args:
            extension: File extension (e.g., ".txt", ".html")
            parser_class: FileParser subclass to handle this extension
        
        Example:
            >>> class HTMLParser(FileParser):
            ...     def parse(self, file_path): ...
            >>> ResumeParserFramework.register_parser(".html", HTMLParser)
        """
        if not extension.startswith("."):
            extension = f".{extension}"
        
        cls.PARSER_REGISTRY[extension.lower()] = parser_class
        logger.info(f"Registered parser {parser_class.__name__} for {extension}")

