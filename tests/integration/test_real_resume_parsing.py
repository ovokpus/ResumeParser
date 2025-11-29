"""Integration tests for parsing real resume documents."""

import os
import pytest
from pathlib import Path
from resume_parser import ResumeParserFramework
from resume_parser.extractors.email_extractor import EmailExtractor
from resume_parser.extractors.skills_extractor import SkillsExtractor
from resume_parser.parsers.pdf_parser import PDFParser
from resume_parser.models import ResumeData


@pytest.mark.integration
class TestRealResumeParsing:
    """Test parsing with actual resume documents."""
    
    @pytest.fixture
    def test_resume_path(self, test_data_dir):
        """Path to test resume file."""
        pdf_path = test_data_dir / "sample_resume.pdf"
        docx_path = test_data_dir / "sample_resume.docx"
        
        # Return whichever exists, or None if neither exists
        if pdf_path.exists():
            return pdf_path
        elif docx_path.exists():
            return docx_path
        return None
    
    def test_pdf_parsing_component(self, test_resume_path):
        """Test PDF parsing to text extraction."""
        if test_resume_path is None:
            pytest.skip("No test resume file found in tests/test_data/")
        
        if test_resume_path.suffix != '.pdf':
            pytest.skip("Test requires PDF file")
        
        parser = PDFParser()
        text = parser.parse(str(test_resume_path))
        
        assert text is not None
        assert len(text) > 0
        assert isinstance(text, str)
    
    def test_email_extraction_from_resume(self, test_resume_path):
        """Test email extraction from real resume."""
        if test_resume_path is None:
            pytest.skip("No test resume file found in tests/test_data/")
        
        parser = PDFParser()
        text = parser.parse(str(test_resume_path))
        
        email_extractor = EmailExtractor()
        email = email_extractor.extract(text)
        
        # Email might not be present, but extractor should work
        if email:
            assert "@" in email
            assert "." in email
    
    @pytest.mark.slow
    def test_skills_extraction_from_resume(self, test_resume_path):
        """Test skills extraction from real resume (requires OpenAI API)."""
        if test_resume_path is None:
            pytest.skip("No test resume file found in tests/test_data/")
        
        if not os.getenv('OPENAI_API_KEY'):
            pytest.skip("OPENAI_API_KEY not set - skipping skills extraction test")
        
        parser = PDFParser()
        text = parser.parse(str(test_resume_path))
        
        skills_extractor = SkillsExtractor()
        skills = skills_extractor.extract(text)
        
        # Skills extraction should return a list (might be empty)
        assert isinstance(skills, list)
    
    @pytest.mark.slow
    def test_full_framework_parsing(self, test_resume_path):
        """Test full framework parsing pipeline."""
        if test_resume_path is None:
            pytest.skip("No test resume file found in tests/test_data/")
        
        if not os.getenv('OPENAI_API_KEY'):
            pytest.skip("OPENAI_API_KEY not set - skipping full parsing test")
        
        framework = ResumeParserFramework()
        result = framework.parse_resume(str(test_resume_path))
        
        assert isinstance(result, ResumeData)
        assert result.name is not None  # Might be empty string
        assert result.email is not None  # Might be empty string
        assert isinstance(result.skills, list)

