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

