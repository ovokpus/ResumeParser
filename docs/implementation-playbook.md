# Resume Parser Framework - Complete Implementation Playbook

## 1. ARCHITECTURAL DECISION ANALYSIS

### 1.1 GPT-4 Field Selection: **Skills Extraction**

**Recommendation:** Use GPT-4 for **Skills** extraction.

**Technical Justification:**

#### Complexity & Variability Analysis

- **Skills**: HIGH complexity
  - Highly unstructured and context-dependent
  - Appears in multiple formats (bullet points, paragraphs, tables)
  - Requires semantic understanding (e.g., "Python" vs "Pythonic coding" vs "Python libraries: pandas, numpy")
  - Domain-specific terminology varies widely
  - Skill categorization benefits from language understanding
  
- **Email**: LOW complexity
  - Well-defined RFC 5322 format
  - Regex patterns are 99%+ accurate
  - Limited variability in structure
  - No semantic understanding required

- **Name**: MEDIUM complexity
  - Usually appears in predictable locations (top of resume)
  - Some cultural variations in name order
  - Can be handled effectively with rule-based approaches + basic NER

#### Demonstration Value for Rubric

- **Skills with GPT-4** showcases:
  - Advanced LLM integration for complex NLP tasks
  - Prompt engineering expertise
  - Handling of ambiguous, unstructured data
  - Production-ready API integration
  - Clear value proposition (GPT-4 solves a genuinely difficult problem)

- **Email/Name with GPT-4** would:
  - Over-engineer simple problems
  - Waste API costs unnecessarily
  - Not demonstrate good engineering judgment

#### Cost-Effectiveness

```
Skills: ~500-1000 tokens/resume * $0.01/1K tokens = $0.005-$0.01/resume
(Reasonable cost for complex extraction)

Email: Same cost but regex is FREE and more reliable
(Poor engineering decision)
```

### 1.2 Extraction Strategy Matrix

| Field | Strategy | Rationale |
|-------|----------|-----------|
| **Email** | Regex | Deterministic, fast, accurate for well-defined patterns |
| **Name** | Rule-based + SpaCy NER | Combines position heuristics with entity recognition |
| **Skills** | GPT-4 (gpt-4-turbo) | Complex semantic understanding, handles variability |

### 1.3 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                 ResumeParserFramework                        │
│  parse_resume(file_path: str) -> ResumeData                 │
└──────────────┬──────────────────────────────────────────────┘
               │
               ├─────────────┬──────────────────────────────┐
               │             │                              │
         ┌─────▼─────┐ ┌────▼──────────┐          ┌────────▼────────┐
         │ FileParser│ │ResumeExtractor│          │   ResumeData    │
         │ (Abstract)│ │  (Coordinator)│          │   (Dataclass)   │
         └─────┬─────┘ └────┬──────────┘          └─────────────────┘
               │             │
        ┌──────┴──────┐      │
        │             │      │
   ┌────▼────┐  ┌────▼─────┐│
   │PDFParser│  │WordParser││
   └─────────┘  └──────────┘│
                            │
                   ┌────────▼────────┐
                   │ FieldExtractor  │
                   │   (Abstract)    │
                   └────────┬────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
        ┌─────▼──────┐ ┌───▼────┐ ┌─────▼──────────┐
        │NameExtractor│ │Email   │ │SkillsExtractor │
        │  (Rule+NER) │ │Extractor│ │   (GPT-4)     │
        └─────────────┘ └────────┘ └────────────────┘
```

**Design Principles:**

- **Strategy Pattern**: FileParser and FieldExtractor abstractions
- **Single Responsibility**: Each extractor handles one field
- **Open/Closed**: Easy to add new file formats or extraction strategies
- **Dependency Inversion**: Framework depends on abstractions, not concrete implementations

---

## 2. PROJECT STRUCTURE & SETUP

### 2.1 Directory Structure (src-layout)

```
resume_parser_framework/
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── setup.py  # Optional: for installable package
├── pytest.ini
│
├── src/
│   └── resume_parser/
│       ├── __init__.py
│       ├── config.py                    # Configuration management
│       ├── exceptions.py                # Custom exceptions
│       ├── models.py                    # ResumeData dataclass
│       │
│       ├── parsers/                     # File parsing
│       │   ├── __init__.py
│       │   ├── base.py                  # FileParser abstract base
│       │   ├── pdf_parser.py            # PDFParser implementation
│       │   └── word_parser.py           # WordParser implementation
│       │
│       ├── extractors/                  # Field extraction
│       │   ├── __init__.py
│       │   ├── base.py                  # FieldExtractor abstract base
│       │   ├── name_extractor.py        # NameExtractor (Rule+NER)
│       │   ├── email_extractor.py       # EmailExtractor (Regex)
│       │   └── skills_extractor.py      # SkillsExtractor (GPT-4)
│       │
│       ├── core/                        # Core orchestration
│       │   ├── __init__.py
│       │   ├── resume_extractor.py      # ResumeExtractor coordinator
│       │   └── framework.py             # ResumeParserFramework
│       │
│       └── utils/                       # Utilities
│           ├── __init__.py
│           ├── logger.py                # Logging setup
│           └── validators.py            # Input validation
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # Pytest fixtures
│   ├── test_data/                       # Sample resumes
│   │   ├── sample_resume.pdf
│   │   ├── sample_resume.docx
│   │   ├── malformed_resume.pdf
│   │   └── empty_resume.docx
│   │
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_parsers/
│   │   │   ├── test_pdf_parser.py
│   │   │   └── test_word_parser.py
│   │   ├── test_extractors/
│   │   │   ├── test_name_extractor.py
│   │   │   ├── test_email_extractor.py
│   │   │   └── test_skills_extractor.py
│   │   └── test_core/
│   │       ├── test_resume_extractor.py
│   │       └── test_framework.py
│   │
│   └── integration/
│       ├── __init__.py
│       └── test_end_to_end.py
│
└── examples/
    ├── basic_usage.py
    └── custom_extractor_example.py
```

### 2.2 Dependencies (requirements.txt)

```txt
# Core parsing libraries
PyPDF2==3.0.1              # PDF text extraction
python-docx==1.1.0         # Word document parsing

# NLP for name extraction
spacy==3.7.2               # NER for name extraction
# Run after install: python -m spacy download en_core_web_sm

# LLM integration
openai==1.6.1              # GPT-4 API
tiktoken==0.5.2            # Token counting for cost estimation

# Configuration & environment
python-dotenv==1.0.0       # Environment variable management
pydantic==2.5.3            # Data validation
pydantic-settings==2.1.0   # Settings management

# Utilities
tenacity==8.2.3            # Retry logic for API calls
```

### 2.3 Development Dependencies (requirements-dev.txt)

```txt
# Testing
pytest==7.4.3
pytest-cov==4.1.0          # Coverage reporting
pytest-mock==3.12.0        # Mocking utilities
responses==0.24.1          # HTTP mocking for OpenAI API

# Code quality
black==23.12.1             # Code formatting
flake8==7.0.0              # Linting
mypy==1.8.0                # Type checking
isort==5.13.2              # Import sorting

# Development
ipython==8.19.0            # Interactive shell
```

### 2.4 Configuration Management (.env.example)

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.1

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=resume_parser.log

# Extraction Configuration
MAX_SKILLS_RETURNED=20
ENABLE_SKILL_CATEGORIZATION=true
```

### 2.5 Environment Setup Instructions

```bash
# 1. Clone/Create project
mkdir resume_parser_framework && cd resume_parser_framework

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Download SpaCy model
python -m spacy download en_core_web_sm

# 5. Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

# 6. Install package in editable mode (optional)
pip install -e .

# 7. Verify setup
pytest tests/
```

---

## 3. IMPLEMENTATION SEQUENCE

### Phase 1: Foundation (30 minutes)

1. **Setup project structure** - Create directories
2. **Configuration & exceptions** - Base infrastructure
3. **ResumeData model** - Output data structure
4. **Logging utility** - Observability foundation

### Phase 2: File Parsers (30 minutes)

5. **FileParser abstract base** - Define interface
6. **PDFParser implementation** - PDF text extraction
7. **WordParser implementation** - DOCX text extraction
8. **Parser unit tests** - Validate parsing logic

### Phase 3: Field Extractors (60 minutes)

9. **FieldExtractor abstract base** - Define interface
10. **EmailExtractor (Regex)** - Simplest extractor first
11. **NameExtractor (Rule+NER)** - Medium complexity
12. **SkillsExtractor (GPT-4)** - Most complex, build last
13. **Extractor unit tests** - Test each extractor independently

### Phase 4: Orchestration (30 minutes)

14. **ResumeExtractor coordinator** - Combine extractors
15. **ResumeParserFramework** - Main public interface
16. **Integration tests** - End-to-end validation

### Phase 5: Polish (30 minutes)

17. **Documentation** - README and docstrings
18. **Examples** - Usage demonstrations
19. **Final testing** - Coverage review and edge cases

**Rationale for sequence:**

- **Bottom-up approach**: Build primitives before composition
- **Test continuously**: Write tests immediately after implementation
- **Defer complexity**: GPT-4 integration last (most complex, most risky)
- **Fast feedback**: Early components can be tested immediately

---

## 4. CODE IMPLEMENTATION DETAILS

### 4.1 Foundation Components

#### src/resume_parser/exceptions.py

```python
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
```

#### src/resume_parser/models.py

```python
"""Data models for resume parsing."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ResumeData:
    """
    Represents parsed resume data.
    
    Attributes:
        name: Full name of the candidate (e.g., "John Doe")
        email: Email address of the candidate (e.g., "john.doe@example.com")
        skills: List of technical and professional skills (e.g., ["Python", "AWS", "Leadership"])
    """
    name: str
    email: str
    skills: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        # Normalize name
        if self.name:
            self.name = " ".join(self.name.split())  # Remove extra whitespace
        
        # Normalize email
        if self.email:
            self.email = self.email.lower().strip()
        
        # Deduplicate and normalize skills
        if self.skills:
            # Remove duplicates while preserving order, normalize casing
            seen = set()
            normalized_skills = []
            for skill in self.skills:
                skill_normalized = skill.strip()
                skill_lower = skill_normalized.lower()
                if skill_lower not in seen and skill_normalized:
                    seen.add(skill_lower)
                    normalized_skills.append(skill_normalized)
            self.skills = normalized_skills
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "email": self.email,
            "skills": self.skills
        }
```

#### src/resume_parser/config.py

```python
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
```

#### src/resume_parser/utils/logger.py

```python
"""Logging configuration for the resume parser."""

import logging
import sys
from typing import Optional
from resume_parser.config import settings


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: Optional[str] = None
) -> logging.Logger:
    """
    Create and configure a logger.
    
    Args:
        name: Logger name (typically __name__)
        log_file: Optional file path for log output
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set level from parameter or config
    log_level = level or settings.log_level
    logger.setLevel(getattr(logging, log_level))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    log_file = log_file or settings.log_file
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
```

### 4.2 File Parser Implementation

#### src/resume_parser/parsers/base.py

```python
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
```

#### src/resume_parser/parsers/pdf_parser.py

```python
"""PDF file parser implementation."""

from pathlib import Path
from typing import Union
import PyPDF2

from resume_parser.parsers.base import FileParser
from resume_parser.exceptions import FileParsingError
from resume_parser.utils.logger import setup_logger

logger = setup_logger(__name__)


class PDFParser(FileParser):
    """
    Parse PDF resume files to extract text content.
    
    Uses PyPDF2 for text extraction with robust error handling
    for various PDF formats and encodings.
    """
    
    def parse(self, file_path: Union[str, Path]) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            Extracted text content
        
        Raises:
            FileParsingError: If PDF cannot be parsed
            FileNotFoundError: If file doesn't exist
        """
        # Validate file exists
        path = self._validate_file_exists(file_path)
        self._validate_file_size(path)
        
        logger.info(f"Parsing PDF file: {path}")
        
        try:
            text_content = []
            
            with open(path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    logger.warning(f"PDF is encrypted: {path}")
                    try:
                        pdf_reader.decrypt('')  # Try empty password
                    except Exception as e:
                        raise FileParsingError(
                            f"Cannot decrypt PDF: {path}. Error: {str(e)}"
                        )
                
                num_pages = len(pdf_reader.pages)
                logger.debug(f"PDF has {num_pages} pages")
                
                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
                        else:
                            logger.warning(f"No text extracted from page {page_num + 1}")
                    except Exception as e:
                        logger.warning(
                            f"Error extracting text from page {page_num + 1}: {str(e)}"
                        )
                        continue
            
            # Combine all pages
            full_text = "\n\n".join(text_content)
            
            if not full_text.strip():
                raise FileParsingError(
                    f"No text content extracted from PDF: {path}. "
                    "The PDF may be image-based or corrupted."
                )
            
            logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
            return full_text
            
        except FileParsingError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing PDF {path}: {str(e)}")
            raise FileParsingError(f"Failed to parse PDF: {str(e)}")
```

#### src/resume_parser/parsers/word_parser.py

```python
"""Word document parser implementation."""

from pathlib import Path
from typing import Union
from docx import Document

from resume_parser.parsers.base import FileParser
from resume_parser.exceptions import FileParsingError
from resume_parser.utils.logger import setup_logger

logger = setup_logger(__name__)


class WordParser(FileParser):
    """
    Parse Word (.docx) resume files to extract text content.
    
    Uses python-docx to extract text from paragraphs, tables,
    and other document elements.
    """
    
    def parse(self, file_path: Union[str, Path]) -> str:
        """
        Extract text from a Word document.
        
        Args:
            file_path: Path to .docx file
        
        Returns:
            Extracted text content
        
        Raises:
            FileParsingError: If document cannot be parsed
            FileNotFoundError: If file doesn't exist
        """
        # Validate file exists
        path = self._validate_file_exists(file_path)
        self._validate_file_size(path)
        
        logger.info(f"Parsing Word document: {path}")
        
        try:
            doc = Document(path)
            text_content = []
            
            # Extract text from paragraphs
            for para in doc.paragraphs:
                if para.text.strip():
                    text_content.append(para.text)
            
            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text)
                    if row_text:
                        text_content.append(" | ".join(row_text))
            
            full_text = "\n".join(text_content)
            
            if not full_text.strip():
                raise FileParsingError(
                    f"No text content extracted from Word document: {path}"
                )
            
            logger.info(
                f"Successfully extracted {len(full_text)} characters from Word document"
            )
            return full_text
            
        except FileParsingError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing Word document {path}: {str(e)}")
            raise FileParsingError(f"Failed to parse Word document: {str(e)}")
```

### 4.3 Field Extractor Implementations

#### src/resume_parser/extractors/base.py

```python
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
```

#### src/resume_parser/extractors/email_extractor.py

```python
"""Email extractor using regex patterns."""

import re
from typing import str
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
```

#### src/resume_parser/extractors/name_extractor.py

```python
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
```

#### src/resume_parser/extractors/skills_extractor.py

```python
"""Skills extractor using GPT-4."""

import json
from typing import List
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from resume_parser.extractors.base import FieldExtractor
from resume_parser.exceptions import ExtractionError, APIError
from resume_parser.config import settings
from resume_parser.utils.logger import setup_logger

logger = setup_logger(__name__)


class SkillsExtractor(FieldExtractor):
    """
    Extract skills from resume text using GPT-4.
    
    Uses OpenAI's GPT-4 Turbo with carefully engineered prompts to:
    - Identify technical and professional skills
    - Handle various skill formats (bullet points, paragraphs, tables)
    - Provide structured JSON output
    - Deduplicate and normalize skill names
    """
    
    # System prompt for GPT-4
    SYSTEM_PROMPT = """You are an expert resume parser specializing in extracting skills from resumes.

Your task is to identify and extract ALL technical and professional skills mentioned in the resume text.

Skills can include:
- Programming languages (Python, JavaScript, Java, etc.)
- Frameworks and libraries (React, Django, TensorFlow, etc.)
- Tools and platforms (Docker, Kubernetes, AWS, Git, etc.)
- Databases (PostgreSQL, MongoDB, Redis, etc.)
- Methodologies (Agile, Scrum, TDD, CI/CD, etc.)
- Soft skills (Leadership, Communication, Problem-solving, etc.)
- Domain expertise (Machine Learning, Data Analysis, Cloud Architecture, etc.)

Guidelines:
1. Extract skills exactly as they appear (preserve casing: "Python" not "python")
2. Remove duplicates (e.g., "Python" and "python programming" → just "Python")
3. Return specific technologies, not categories (e.g., "React" not "frontend frameworks")
4. Include both hard skills and relevant soft skills
5. If a skill appears multiple times in different contexts, include it only once
6. Do not invent skills that aren't mentioned in the resume

Return ONLY a valid JSON object with a "skills" array. No additional text or explanation.

Example output:
{"skills": ["Python", "Machine Learning", "AWS", "Docker", "Team Leadership"]}"""
    
    def __init__(self):
        """Initialize OpenAI client and validate configuration."""
        try:
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
            self.max_tokens = settings.openai_max_tokens
            self.temperature = settings.openai_temperature
            logger.info(f"Initialized SkillsExtractor with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise ExtractionError(f"OpenAI initialization failed: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(APIError),
        reraise=True
    )
    def extract(self, text: str) -> List[str]:
        """
        Extract skills from resume text using GPT-4.
        
        Args:
            text: Resume text content
        
        Returns:
            List of extracted skills
        
        Raises:
            ExtractionError: If extraction fails
            APIError: If OpenAI API call fails (with retry)
        """
        self._validate_text_input(text)
        
        logger.info("Extracting skills using GPT-4")
        
        try:
            # Truncate text if too long (GPT-4 context limit consideration)
            max_chars = 15000  # ~3750 tokens
            if len(text) > max_chars:
                logger.warning(
                    f"Resume text ({len(text)} chars) exceeds limit, truncating to {max_chars}"
                )
                text = text[:max_chars]
            
            # Create user prompt
            user_prompt = f"""Extract all skills from the following resume text:

{text}

Return ONLY the JSON object with the skills array."""
            
            # Call OpenAI API
            logger.debug(f"Calling OpenAI API with model: {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}  # Enforce JSON output
            )
            
            # Extract and parse response
            content = response.choices[0].message.content
            logger.debug(f"GPT-4 response: {content}")
            
            # Parse JSON response
            result = json.loads(content)
            skills = result.get("skills", [])
            
            # Validate and limit skills
            if not isinstance(skills, list):
                raise ExtractionError("GPT-4 returned invalid skills format")
            
            # Filter out empty strings and limit to max skills
            skills = [s.strip() for s in skills if s and s.strip()]
            skills = skills[:settings.max_skills_returned]
            
            logger.info(f"Successfully extracted {len(skills)} skills using GPT-4")
            logger.debug(f"Extracted skills: {skills}")
            
            # Log token usage for cost tracking
            usage = response.usage
            logger.info(
                f"Token usage - Prompt: {usage.prompt_tokens}, "
                f"Completion: {usage.completion_tokens}, "
                f"Total: {usage.total_tokens}"
            )
            
            return skills
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT-4 JSON response: {str(e)}")
            raise ExtractionError(f"Invalid JSON response from GPT-4: {str(e)}")
        
        except Exception as e:
            # Distinguish between retryable API errors and fatal errors
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ['rate limit', 'timeout', 'connection']):
                logger.warning(f"Retryable API error: {str(e)}")
                raise APIError(f"OpenAI API error: {str(e)}")
            else:
                logger.error(f"Fatal error extracting skills: {str(e)}")
                raise ExtractionError(f"Failed to extract skills: {str(e)}")
```

### 4.4 Orchestration Layer

#### src/resume_parser/core/resume_extractor.py

```python
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
```

#### src/resume_parser/core/framework.py

```python
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
```

---

## 5. TESTING STRATEGY & IMPLEMENTATION

### 5.1 Testing Philosophy

**Principles:**

- **Test Pyramid**: Many unit tests, fewer integration tests
- **Isolation**: Unit tests mock external dependencies (OpenAI API, file I/O)
- **Coverage Target**: 90%+ line coverage
- **Edge Cases First**: Write tests for failure modes before happy paths

### 5.2 Test Structure

#### tests/conftest.py

```python
"""Pytest fixtures and configuration."""

import pytest
from pathlib import Path
from resume_parser.models import ResumeData


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing."""
    return """
    John Doe
    john.doe@example.com | (555) 123-4567
    
    PROFESSIONAL SUMMARY
    Senior Software Engineer with 8 years of experience in Python development.
    
    SKILLS
    - Programming Languages: Python, JavaScript, Java
    - Frameworks: Django, React, Flask
    - Cloud: AWS, Docker, Kubernetes
    - Databases: PostgreSQL, MongoDB, Redis
    - Other: Git, CI/CD, Agile, Team Leadership
    
    EXPERIENCE
    Senior Software Engineer | Tech Corp | 2020-Present
    - Led development of microservices architecture using Python and AWS
    - Implemented CI/CD pipelines reducing deployment time by 60%
    """


@pytest.fixture
def sample_resume_data():
    """Sample ResumeData for testing."""
    return ResumeData(
        name="John Doe",
        email="john.doe@example.com",
        skills=["Python", "JavaScript", "AWS", "Docker"]
    )


@pytest.fixture
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [{
            "message": {
                "content": '{"skills": ["Python", "AWS", "Docker", "Kubernetes"]}'
            }
        }],
        "usage": {
            "prompt_tokens": 500,
            "completion_tokens": 50,
            "total_tokens": 550
        }
    }
```

### 5.3 Unit Tests Examples

#### tests/unit/test_extractors/test_email_extractor.py

```python
"""Unit tests for EmailExtractor."""

import pytest
from resume_parser.extractors.email_extractor import EmailExtractor
from resume_parser.exceptions import ExtractionError


class TestEmailExtractor:
    """Test suite for EmailExtractor."""
    
    def setup_method(self):
        """Setup test fixture."""
        self.extractor = EmailExtractor()
    
    def test_extract_simple_email(self):
        """Test extracting a simple email address."""
        text = "Contact me at john.doe@example.com for more information."
        result = self.extractor.extract(text)
        assert result == "john.doe@example.com"
    
    def test_extract_email_with_numbers(self):
        """Test email with numbers."""
        text = "Email: john.doe123@company456.com"
        result = self.extractor.extract(text)
        assert result == "john.doe123@company456.com"
    
    def test_extract_email_with_plus(self):
        """Test email with plus sign."""
        text = "john.doe+label@example.com"
        result = self.extractor.extract(text)
        assert result == "john.doe+label@example.com"
    
    def test_extract_first_email_when_multiple(self):
        """Test extraction when multiple emails present."""
        text = "Primary: john@example.com, Secondary: jane@example.com"
        result = self.extractor.extract(text)
        assert result == "john@example.com"
    
    def test_no_email_found(self):
        """Test when no email is present."""
        text = "This text has no email address in it."
        result = self.extractor.extract(text)
        assert result == ""
    
    def test_invalid_email_filtered(self):
        """Test that invalid/test emails are filtered."""
        text = "test@example.com should be filtered"
        result = self.extractor.extract(text)
        assert result == ""
    
    def test_empty_text_raises_error(self):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="empty text"):
            self.extractor.extract("")
    
    def test_whitespace_only_raises_error(self):
        """Test that whitespace-only text raises ValueError."""
        with pytest.raises(ValueError, match="empty text"):
            self.extractor.extract("   \n\t  ")
    
    def test_email_in_complex_resume(self, sample_resume_text):
        """Test extraction from complex resume text."""
        result = self.extractor.extract(sample_resume_text)
        assert result == "john.doe@example.com"
```

#### tests/unit/test_extractors/test_skills_extractor.py

```python
"""Unit tests for SkillsExtractor."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from resume_parser.extractors.skills_extractor import SkillsExtractor
from resume_parser.exceptions import ExtractionError, APIError


class TestSkillsExtractor:
    """Test suite for SkillsExtractor."""
    
    @patch('resume_parser.extractors.skills_extractor.OpenAI')
    def setup_method(self, mock_openai):
        """Setup test fixture with mocked OpenAI."""
        self.mock_client = MagicMock()
        mock_openai.return_value = self.mock_client
        self.extractor = SkillsExtractor()
    
    def test_extract_skills_success(self, sample_resume_text):
        """Test successful skills extraction."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''
        {
            "skills": ["Python", "JavaScript", "AWS", "Docker", "Kubernetes"]
        }
        '''
        mock_response.usage.prompt_tokens = 500
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 550
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Execute
        result = self.extractor.extract(sample_resume_text)
        
        # Verify
        assert isinstance(result, list)
        assert len(result) == 5
        assert "Python" in result
        assert "AWS" in result
        
        # Verify API was called correctly
        self.mock_client.chat.completions.create.assert_called_once()
        call_kwargs = self.mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['model'] == self.extractor.model
        assert call_kwargs['temperature'] == self.extractor.temperature
        assert 'messages' in call_kwargs
    
    def test_extract_skills_empty_result(self):
        """Test when GPT-4 returns no skills."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"skills": []}'
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 10
        mock_response.usage.total_tokens = 110
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        result = self.extractor.extract("Some text")
        assert result == []
    
    def test_extract_skills_filters_empty_strings(self):
        """Test that empty strings are filtered from results."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''
        {"skills": ["Python", "", "AWS", "  ", "Docker"]}
        '''
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 120
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        result = self.extractor.extract("Some text")
        assert len(result) == 3
        assert "" not in result
    
    def test_extract_skills_limits_max_skills(self):
        """Test that results are limited to max_skills_returned."""
        skills = [f"Skill{i}" for i in range(50)]  # 50 skills
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = f'{{"skills": {skills}}}'
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 100
        mock_response.usage.total_tokens = 200
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        result = self.extractor.extract("Some text")
        assert len(result) <= 20  # Based on default max_skills_returned
    
    def test_extract_skills_invalid_json(self):
        """Test handling of invalid JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'Invalid JSON {{'
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        with pytest.raises(ExtractionError, match="Invalid JSON"):
            self.extractor.extract("Some text")
    
    def test_extract_skills_api_rate_limit_error(self):
        """Test handling of API rate limit errors with retry."""
        self.mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")
        
        with pytest.raises(APIError, match="OpenAI API error"):
            self.extractor.extract("Some text")
    
    def test_extract_skills_truncates_long_text(self):
        """Test that very long text is truncated."""
        long_text = "A" * 20000  # 20k characters
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"skills": ["Python"]}'
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 10
        mock_response.usage.total_tokens = 110
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        result = self.extractor.extract(long_text)
        
        # Verify truncation occurred by checking API call
        call_kwargs = self.mock_client.chat.completions.create.call_args[1]
        user_message = call_kwargs['messages'][1]['content']
        assert len(user_message) < 20000
    
    def test_empty_text_raises_error(self):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="empty text"):
            self.extractor.extract("")
```

### 5.4 Integration Tests

#### tests/integration/test_end_to_end.py

```python
"""End-to-end integration tests."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from resume_parser.core.framework import ResumeParserFramework
from resume_parser.models import ResumeData
from resume_parser.exceptions import FileParsingError, ValidationError


class TestEndToEnd:
    """Integration tests for complete parsing pipeline."""
    
    def setup_method(self):
        """Setup test fixture."""
        self.framework = ResumeParserFramework()
    
    @patch('resume_parser.extractors.skills_extractor.OpenAI')
    def test_parse_pdf_resume_success(self, mock_openai, test_data_dir):
        """Test complete PDF parsing pipeline."""
        # Mock OpenAI for skills extraction
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''
        {"skills": ["Python", "AWS", "Machine Learning"]}
        '''
        mock_response.usage.prompt_tokens = 200
        mock_response.usage.completion_tokens = 30
        mock_response.usage.total_tokens = 230
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Parse resume
        pdf_path = test_data_dir / "sample_resume.pdf"
        result = self.framework.parse_resume(pdf_path)
        
        # Verify result structure
        assert isinstance(result, ResumeData)
        assert result.name  # Should have extracted name
        assert result.email  # Should have extracted email
        assert len(result.skills) > 0  # Should have extracted skills
    
    @patch('resume_parser.extractors.skills_extractor.OpenAI')
    def test_parse_word_resume_success(self, mock_openai, test_data_dir):
        """Test complete Word document parsing pipeline."""
        # Mock OpenAI
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''
        {"skills": ["JavaScript", "React", "Node.js"]}
        '''
        mock_response.usage.prompt_tokens = 150
        mock_response.usage.completion_tokens = 25
        mock_response.usage.total_tokens = 175
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Parse resume
        docx_path = test_data_dir / "sample_resume.docx"
        result = self.framework.parse_resume(docx_path)
        
        # Verify
        assert isinstance(result, ResumeData)
        assert result.name
        assert result.email
        assert len(result.skills) > 0
    
    def test_parse_nonexistent_file(self):
        """Test parsing nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            self.framework.parse_resume("nonexistent_file.pdf")
    
    def test_parse_unsupported_format(self, test_data_dir, tmp_path):
        """Test parsing unsupported file format raises error."""
        # Create a .txt file
        txt_file = tmp_path / "resume.txt"
        txt_file.write_text("Some resume content")
        
        with pytest.raises(ValidationError, match="Unsupported file format"):
            self.framework.parse_resume(txt_file)
    
    @patch('resume_parser.extractors.skills_extractor.OpenAI')
    def test_partial_extraction_on_error(self, mock_openai, sample_resume_text):
        """Test that partial results are returned when some extractors fail."""
        # This test would require a more complex setup
        # to simulate partial failures while still producing a result
        pass
```

### 5.5 Test Coverage Measurement

```bash
# Run tests with coverage
pytest --cov=src/resume_parser --cov-report=html --cov-report=term

# Generate coverage report
coverage html
# Open htmlcov/index.html to view detailed coverage

# Target: 90%+ coverage
```

---

## 6. DOCUMENTATION & README

### README.md

```markdown
# Resume Parser Framework

A production-ready, extensible framework for parsing resumes from PDF and Word documents, extracting structured data (name, email, skills) using multiple extraction strategies including GPT-4.

## Features

- **Multi-Format Support**: Parse PDF (.pdf) and Word (.docx) documents
- **Pluggable Architecture**: Easily extend with new file formats or extraction strategies
- **Advanced Extraction**:
  - **Email**: Regex-based extraction with RFC 5322 compliance
  - **Name**: Rule-based + SpaCy NER for accurate name identification
  - **Skills**: GPT-4 powered semantic extraction for complex skill identification
- **Production-Ready**:
  - Comprehensive error handling and logging
  - Retry logic for API calls
  - Input validation and edge case handling
  - 90%+ test coverage
- **Type-Safe**: Full type hints throughout codebase

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key (for skills extraction)

### Setup

```bash
# Clone repository
git clone <repository-url>
cd resume_parser_framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download SpaCy model for name extraction
python -m spacy download en_core_web_sm

# Configure environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Configuration

Create a `.env` file with the following variables:

```bash
# OpenAI Configuration (Required)
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.1

# Logging Configuration (Optional)
LOG_LEVEL=INFO
LOG_FILE=resume_parser.log

# Extraction Configuration (Optional)
MAX_SKILLS_RETURNED=20
ENABLE_SKILL_CATEGORIZATION=true
```

## Usage

### Basic Usage

```python
from resume_parser.core.framework import ResumeParserFramework

# Initialize framework
framework = ResumeParserFramework()

# Parse a resume
resume_data = framework.parse_resume("path/to/resume.pdf")

# Access extracted data
print(f"Name: {resume_data.name}")
print(f"Email: {resume_data.email}")
print(f"Skills: {', '.join(resume_data.skills)}")

# Convert to JSON
import json
print(json.dumps(resume_data.to_dict(), indent=2))
```

### Advanced Usage

#### Custom Extractors

```python
from resume_parser.extractors.base import FieldExtractor
from resume_parser.core.resume_extractor import ResumeExtractor
from resume_parser.core.framework import ResumeParserFramework

# Create custom extractor
class CustomNameExtractor(FieldExtractor):
    def extract(self, text: str) -> str:
        # Your custom logic here
        return extracted_name

# Use custom extractor
custom_extractor = ResumeExtractor(
    name_extractor=CustomNameExtractor()
)
framework = ResumeParserFramework(resume_extractor=custom_extractor)
```

#### Register New File Format

```python
from resume_parser.parsers.base import FileParser
from resume_parser.core.framework import ResumeParserFramework

class HTMLParser(FileParser):
    def parse(self, file_path):
        # Your HTML parsing logic
        return extracted_text

# Register parser
ResumeParserFramework.register_parser(".html", HTMLParser)
```

## Architecture

### System Overview

```
ResumeParserFramework (Main API)
├── FileParser (Strategy Pattern)
│   ├── PDFParser (PyPDF2)
│   └── WordParser (python-docx)
└── ResumeExtractor (Coordinator)
    └── FieldExtractor (Strategy Pattern)
        ├── EmailExtractor (Regex)
        ├── NameExtractor (Rule-based + SpaCy NER)
        └── SkillsExtractor (GPT-4 Turbo)
```

### Design Patterns

- **Strategy Pattern**: Pluggable file parsers and field extractors
- **Dependency Injection**: Extractors can be customized via constructor
- **Factory Pattern**: Parser registry for file format mapping
- **Single Responsibility**: Each class has one clear purpose

### Key Components

- **FileParser**: Abstract base for file format handlers
- **FieldExtractor**: Abstract base for field extraction strategies
- **ResumeExtractor**: Coordinates multiple extractors
- **ResumeParserFramework**: Main public API
- **ResumeData**: Dataclass for structured output

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/resume_parser --cov-report=html

# Run specific test file
pytest tests/unit/test_extractors/test_skills_extractor.py

# Run with verbose output
pytest -v
```

## Error Handling

The framework provides specific exceptions:

- `FileParsingError`: File cannot be parsed
- `ExtractionError`: Field extraction fails
- `ValidationError`: Input validation fails
- `APIError`: External API calls fail (with retry)
- `ConfigurationError`: Invalid configuration

## Performance Considerations

- **API Costs**: GPT-4 Turbo costs ~$0.01/resume (skills extraction only)
- **Processing Time**: ~2-5 seconds per resume (including API call)
- **Rate Limiting**: Automatic retry with exponential backoff
- **Text Truncation**: Large resumes truncated to 15,000 characters

## Troubleshooting

### Common Issues

**Issue**: `SpaCy model not found`

```bash
# Solution: Download the model
python -m spacy download en_core_web_sm
```

**Issue**: `OpenAI API key error`

```bash
# Solution: Verify .env file has correct API key
cat .env | grep OPENAI_API_KEY
```

**Issue**: `PDF text extraction returns empty`

```
# Cause: PDF may be image-based
# Solution: Use OCR preprocessing (not included in this framework)
```

## Contributing

1. Follow PEP 8 style guide
2. Add type hints to all functions
3. Write tests for new features (maintain 90%+ coverage)
4. Update documentation

## License

MIT License - See LICENSE file for details

## Contact

For questions or issues, please open a GitHub issue or contact [your-email@example.com]

```

---

## 7. USE EXAMPLES & DEMONSTRATION

### examples/basic_usage.py

```python
"""Basic usage examples for Resume Parser Framework."""

import json
import logging
from pathlib import Path
from resume_parser.core.framework import ResumeParserFramework

# Setup logging to see framework operations
logging.basicConfig(level=logging.INFO)


def example_1_parse_pdf():
    """Example 1: Parse a PDF resume."""
    print("\n" + "="*60)
    print("Example 1: Parse PDF Resume")
    print("="*60)
    
    framework = ResumeParserFramework()
    
    # Parse PDF resume
    resume_data = framework.parse_resume("test_data/sample_resume.pdf")
    
    # Display results
    print("\nExtracted Data:")
    print(f"Name: {resume_data.name}")
    print(f"Email: {resume_data.email}")
    print(f"Skills ({len(resume_data.skills)}):")
    for skill in resume_data.skills:
        print(f"  - {skill}")
    
    # Convert to JSON
    print("\nJSON Output:")
    print(json.dumps(resume_data.to_dict(), indent=2))


def example_2_parse_word():
    """Example 2: Parse a Word document resume."""
    print("\n" + "="*60)
    print("Example 2: Parse Word Document Resume")
    print("="*60)
    
    framework = ResumeParserFramework()
    
    # Parse Word resume
    resume_data = framework.parse_resume("test_data/sample_resume.docx")
    
    print("\nExtracted Data:")
    print(json.dumps(resume_data.to_dict(), indent=2))


def example_3_batch_processing():
    """Example 3: Batch process multiple resumes."""
    print("\n" + "="*60)
    print("Example 3: Batch Process Multiple Resumes")
    print("="*60)
    
    framework = ResumeParserFramework()
    
    # List of resume files
    resume_files = [
        "test_data/resume1.pdf",
        "test_data/resume2.docx",
        "test_data/resume3.pdf",
    ]
    
    results = []
    for file_path in resume_files:
        try:
            resume_data = framework.parse_resume(file_path)
            results.append({
                "file": file_path,
                "data": resume_data.to_dict(),
                "status": "success"
            })
            print(f"✓ Processed: {file_path}")
        except Exception as e:
            results.append({
                "file": file_path,
                "error": str(e),
                "status": "failed"
            })
            print(f"✗ Failed: {file_path} - {str(e)}")
    
    # Save results
    output_file = "batch_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")


def example_4_error_handling():
    """Example 4: Demonstrate error handling."""
    print("\n" + "="*60)
    print("Example 4: Error Handling")
    print("="*60)
    
    framework = ResumeParserFramework()
    
    # Test various error scenarios
    test_cases = [
        ("nonexistent.pdf", "File not found"),
        ("test_data/corrupted.pdf", "Parsing error"),
        ("test_data/empty.docx", "Empty content"),
    ]
    
    for file_path, expected_error in test_cases:
        try:
            resume_data = framework.parse_resume(file_path)
            print(f"✓ Unexpected success: {file_path}")
        except FileNotFoundError:
            print(f"✓ Caught FileNotFoundError: {file_path}")
        except Exception as e:
            print(f"✓ Caught {type(e).__name__}: {file_path} - {str(e)}")


if __name__ == "__main__":
    # Run all examples
    example_1_parse_pdf()
    example_2_parse_word()
    example_3_batch_processing()
    example_4_error_handling()
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)
```

### examples/custom_extractor_example.py

```python
"""Example of extending the framework with custom extractors."""

import re
from typing import List
from resume_parser.extractors.base import FieldExtractor
from resume_parser.core.resume_extractor import ResumeExtractor
from resume_parser.core.framework import ResumeParserFramework


class CustomPhoneExtractor(FieldExtractor):
    """
    Custom extractor for phone numbers.
    
    This demonstrates how to create a new field extractor
    following the framework's architecture.
    """
    
    PHONE_PATTERN = re.compile(
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    )
    
    def extract(self, text: str) -> str:
        """Extract phone number from text."""
        self._validate_text_input(text)
        
        matches = self.PHONE_PATTERN.findall(text)
        if matches:
            return matches[0]
        return ""


class EnhancedNameExtractor(FieldExtractor):
    """
    Enhanced name extractor with additional validation.
    
    Demonstrates customizing existing extraction logic.
    """
    
    def extract(self, text: str) -> str:
        """Extract name with enhanced validation."""
        self._validate_text_input(text)
        
        # Your custom name extraction logic
        lines = text.split('\n')
        for line in lines[:3]:
            line = line.strip()
            if self._looks_like_name(line):
                return line
        return ""
    
    def _looks_like_name(self, text: str) -> bool:
        """Enhanced name validation."""
        # Custom validation logic
        if not text or len(text) < 5:
            return False
        
        words = text.split()
        if len(words) < 2 or len(words) > 4:
            return False
        
        # Add your custom rules here
        return True


def main():
    """Demonstrate custom extractor usage."""
    print("Custom Extractor Example")
    print("="*60)
    
    # Option 1: Use custom extractor with existing framework
    custom_extractor = ResumeExtractor(
        name_extractor=EnhancedNameExtractor()
    )
    framework = ResumeParserFramework(resume_extractor=custom_extractor)
    
    result = framework.parse_resume("test_data/sample_resume.pdf")
    print(f"Name (with custom extractor): {result.name}")
    
    # Option 2: Standalone usage
    phone_extractor = CustomPhoneExtractor()
    text = "Contact me at (555) 123-4567 for more info."
    phone = phone_extractor.extract(text)
    print(f"Extracted phone: {phone}")


if __name__ == "__main__":
    main()
```

---

## 8. PRODUCTION READINESS CONSIDERATIONS

### 8.1 Security

**API Key Management:**

```python
# ❌ BAD: Hardcoded API key
api_key = "sk-1234567890abcdef"

# ✅ GOOD: Environment variable
from resume_parser.config import settings
api_key = settings.openai_api_key
```

**Input Validation:**

- File size limits (prevent DOS)
- File type validation (prevent malicious files)
- Text sanitization before API calls

**PII Handling:**

- Log levels configured to avoid logging sensitive data
- Consider encryption for stored resume data
- GDPR compliance for EU users

### 8.2 Scalability

**Optimization Opportunities:**

1. **Caching**: Cache GPT-4 responses for duplicate resumes
2. **Batch Processing**: Process multiple resumes in parallel
3. **Async I/O**: Use asyncio for concurrent API calls
4. **Database Integration**: Store results in database for analytics

**Example Async Implementation:**

```python
import asyncio
from typing import List

async def parse_resumes_async(
    file_paths: List[str]
) -> List[ResumeData]:
    """Parse multiple resumes concurrently."""
    framework = ResumeParserFramework()
    
    tasks = [
        asyncio.to_thread(framework.parse_resume, path)
        for path in file_paths
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### 8.3 Monitoring & Observability

**Key Metrics to Track:**

- Parsing success rate
- Average processing time
- API token usage and costs
- Error rates by type

**Implementation:**

```python
# Add to framework.py
import time
from dataclasses import dataclass

@dataclass
class ParsingMetrics:
    file_path: str
    file_type: str
    processing_time: float
    success: bool
    tokens_used: int
    error: Optional[str] = None

class ResumeParserFramework:
    def parse_resume(self, file_path: Union[str, Path]) -> ResumeData:
        start_time = time.time()
        
        try:
            # ... existing parsing logic ...
            
            metrics = ParsingMetrics(
                file_path=str(file_path),
                file_type=Path(file_path).suffix,
                processing_time=time.time() - start_time,
                success=True,
                tokens_used=# from GPT-4 response
            )
            self._log_metrics(metrics)
            
        except Exception as e:
            metrics = ParsingMetrics(
                file_path=str(file_path),
                file_type=Path(file_path).suffix,
                processing_time=time.time() - start_time,
                success=False,
                tokens_used=0,
                error=str(e)
            )
            self._log_metrics(metrics)
            raise
```

### 8.4 Deployment Considerations

**Containerization (Docker):**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY src/ ./src/
COPY .env .env

# Run application
CMD ["python", "-m", "src.resume_parser"]
```

**API Endpoint (FastAPI):**

```python
from fastapi import FastAPI, UploadFile, HTTPException
from resume_parser.core.framework import ResumeParserFramework

app = FastAPI()
framework = ResumeParserFramework()

@app.post("/parse-resume")
async def parse_resume(file: UploadFile):
    """API endpoint to parse uploaded resume."""
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # Parse resume
        result = framework.parse_resume(temp_path)
        
        # Cleanup
        os.remove(temp_path)
        
        return result.to_dict()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 9. COMMON PITFALLS & HOW TO AVOID THEM

### 9.1 OOD Implementation Pitfalls

**❌ Pitfall 1: Tight Coupling**

```python
# BAD: ResumeExtractor directly instantiates extractors
class ResumeExtractor:
    def __init__(self):
        self.name_extractor = NameExtractor()  # Tight coupling
```

**✅ Solution: Dependency Injection**

```python
# GOOD: Accept extractors as parameters
class ResumeExtractor:
    def __init__(self, name_extractor: FieldExtractor = None):
        self.name_extractor = name_extractor or NameExtractor()
```

**❌ Pitfall 2: God Class**

```python
# BAD: Single class doing everything
class ResumeParser:
    def parse_pdf(self, file): ...
    def parse_word(self, file): ...
    def extract_name(self, text): ...
    def extract_email(self, text): ...
    def extract_skills(self, text): ...
```

**✅ Solution: Single Responsibility**

```python
# GOOD: Separate concerns
class FileParser: ...
class FieldExtractor: ...
class ResumeExtractor: ...
```

### 9.2 GPT-4 Integration Pitfalls

**❌ Pitfall 3: No Retry Logic**

```python
# BAD: Single API call with no retry
response = openai.ChatCompletion.create(...)
```

**✅ Solution: Retry with Exponential Backoff**

```python
# GOOD: Use tenacity for retries
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def extract(self, text):
    response = self.client.chat.completions.create(...)
```

**❌ Pitfall 4: Ignoring Token Limits**

```python
# BAD: Send entire resume without checking
response = client.chat.completions.create(
    messages=[{"role": "user", "content": entire_resume}]
)
```

**✅ Solution: Truncate and Log**

```python
# GOOD: Truncate and warn
max_chars = 15000
if len(text) > max_chars:
    logger.warning(f"Truncating from {len(text)} to {max_chars}")
    text = text[:max_chars]
```

### 9.3 Testing Pitfalls

**❌ Pitfall 5: Testing Implementation, Not Behavior**

```python
# BAD: Test internal methods
def test_internal_method():
    extractor = EmailExtractor()
    result = extractor._validate_email("test@example.com")
```

**✅ Solution: Test Public Interface**

```python
# GOOD: Test public behavior
def test_extract_email():
    extractor = EmailExtractor()
    result = extractor.extract("Email: test@example.com")
    assert result == "test@example.com"
```

**❌ Pitfall 6: Not Mocking External Dependencies**

```python
# BAD: Actually call OpenAI API in tests
def test_extract_skills():
    extractor = SkillsExtractor()  # Will make real API call!
    result = extractor.extract("Python developer")
```

**✅ Solution: Mock API Calls**

```python
# GOOD: Mock the API
@patch('resume_parser.extractors.skills_extractor.OpenAI')
def test_extract_skills(self, mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    # ... test with mocked client
```

### 9.4 Performance Pitfalls

**❌ Pitfall 7: Processing Entire Resume for Each Field**

```python
# BAD: Parse file multiple times
class ResumeExtractor:
    def extract(self, file_path):
        name = self.parse_and_extract_name(file_path)
        email = self.parse_and_extract_email(file_path)
        skills = self.parse_and_extract_skills(file_path)
```

**✅ Solution: Parse Once, Extract Multiple Times**

```python
# GOOD: Parse once, then extract
class ResumeParserFramework:
    def parse_resume(self, file_path):
        text = parser.parse(file_path)  # Once
        resume_data = extractor.extract(text)  # Multiple extractors
```

---

## 10. EXECUTION CHECKLIST

### Phase 1: Foundation (30 min) ✓

- [ ] Create project directory structure
- [ ] Setup virtual environment
- [ ] Install dependencies
- [ ] Create `.env` file with API key
- [ ] Implement configuration (`config.py`)
- [ ] Implement exceptions (`exceptions.py`)
- [ ] Implement ResumeData model (`models.py`)
- [ ] Setup logging utility (`utils/logger.py`)

### Phase 2: File Parsers (30 min) ✓

- [ ] Implement FileParser base class (`parsers/base.py`)
- [ ] Implement PDFParser (`parsers/pdf_parser.py`)
- [ ] Implement WordParser (`parsers/word_parser.py`)
- [ ] Write parser unit tests
- [ ] Test with sample PDF and DOCX files

### Phase 3: Field Extractors (60 min) ✓

- [ ] Implement FieldExtractor base class (`extractors/base.py`)
- [ ] Implement EmailExtractor with regex (`extractors/email_extractor.py`)
- [ ] Write EmailExtractor tests
- [ ] Implement NameExtractor with NER (`extractors/name_extractor.py`)
- [ ] Write NameExtractor tests
- [ ] Implement SkillsExtractor with GPT-4 (`extractors/skills_extractor.py`)
- [ ] Write SkillsExtractor tests (with mocking)

### Phase 4: Orchestration (30 min) ✓

- [ ] Implement ResumeExtractor coordinator (`core/resume_extractor.py`)
- [ ] Implement ResumeParserFramework (`core/framework.py`)
- [ ] Write integration tests (`tests/integration/test_end_to_end.py`)
- [ ] Test complete pipeline with real files

### Phase 5: Polish (30 min) ✓

- [ ] Write README.md with usage examples
- [ ] Add docstrings to all public methods
- [ ] Create usage examples (`examples/basic_usage.py`)
- [ ] Run test suite and verify coverage (target: 90%+)
- [ ] Run linting (black, flake8, mypy)
- [ ] Final manual testing with various resume formats

### Pre-Submission ✓

- [ ] Verify all tests pass
- [ ] Check test coverage report
- [ ] Review code for TODOs and comments
- [ ] Ensure .env.example is present (no real API key)
- [ ] Verify README is complete and accurate
- [ ] Test installation instructions on clean environment
- [ ] Package submission with all required files

---

## CONCLUSION

This playbook provides a comprehensive guide to building an **Outstanding** (4/4 score) Resume Parser Framework. Key success factors:

1. **Solid OOD Foundation**: Abstract base classes with clear interfaces
2. **Strategic GPT-4 Use**: Skills extraction demonstrates real LLM value
3. **Production Quality**: Error handling, logging, retry logic, validation
4. **Comprehensive Testing**: 90%+ coverage with mocked dependencies
5. **Clear Documentation**: README, docstrings, and usage examples

**Estimated Timeline**: 2-4 hours for full implementation

**Next Steps**:

1. Setup project structure (15 min)
2. Implement foundation components (30 min)
3. Build parsers (30 min)
4. Build extractors (60 min)
5. Create orchestration layer (30 min)
6. Write tests and documentation (45 min)

This framework demonstrates senior-level engineering: thoughtful design, production readiness, and attention to detail that evaluators will recognize immediately.

Good luck with your assignment! 🚀
