"""Integration test to verify framework setup and configuration."""

import os
import pytest
from resume_parser import ResumeParserFramework, ResumeData


@pytest.mark.integration
class TestSetupVerification:
    """Verify that the framework is properly set up."""
    
    def test_imports(self):
        """Test that core components can be imported."""
        from resume_parser import ResumeParserFramework, ResumeData
        from resume_parser.extractors.email_extractor import EmailExtractor
        from resume_parser.extractors.skills_extractor import SkillsExtractor
        from resume_parser.parsers.pdf_parser import PDFParser
        
        assert ResumeParserFramework is not None
        assert ResumeData is not None
        assert EmailExtractor is not None
        assert SkillsExtractor is not None
        assert PDFParser is not None
    
    def test_environment_variables(self):
        """Test that required environment variables are documented."""
        # Note: We don't require OPENAI_API_KEY to be set for tests
        # but we verify the environment check works
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            # Verify it's a valid format (starts with sk-)
            assert api_key.startswith('sk-') or len(api_key) > 10
    
    def test_spacy_model(self):
        """Test that SpaCy model can be loaded (if installed)."""
        try:
            import spacy
            try:
                nlp = spacy.load("en_core_web_sm")
                assert nlp is not None
            except OSError:
                pytest.skip("SpaCy model 'en_core_web_sm' not installed")
        except ImportError:
            pytest.skip("SpaCy not installed")
    
    def test_resume_data_model(self):
        """Test that ResumeData model works correctly."""
        resume_data = ResumeData(
            name="John Doe",
            email="john.doe@example.com",
            skills=["Python", "AWS", "Docker"]
        )
        
        assert resume_data.name == "John Doe"
        assert resume_data.email == "john.doe@example.com"
        assert len(resume_data.skills) == 3
        assert "Python" in resume_data.skills
        
        # Test serialization
        data_dict = resume_data.to_dict()
        assert data_dict["name"] == "John Doe"
        assert data_dict["email"] == "john.doe@example.com"
        assert isinstance(data_dict["skills"], list)
    
    def test_framework_initialization(self):
        """Test that framework can be initialized."""
        framework = ResumeParserFramework()
        assert framework is not None
        assert hasattr(framework, 'parse_resume')

