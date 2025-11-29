"""Unit tests for ResumeParserFramework."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from resume_parser.core.framework import ResumeParserFramework
from resume_parser.exceptions import ValidationError
from resume_parser.parsers.base import FileParser


class TestResumeParserFramework:
    """Test suite for ResumeParserFramework."""
    
    def setup_method(self):
        """Setup test fixture."""
        self.framework = ResumeParserFramework()
    
    def test_initialization(self):
        """Test framework initialization."""
        assert self.framework is not None
        assert self.framework.resume_extractor is not None
    
    def test_unsupported_file_format(self, tmp_path):
        """Test that unsupported file format raises error."""
        # Create a .txt file
        txt_file = tmp_path / "resume.txt"
        txt_file.write_text("Some resume content")
        
        with pytest.raises(ValidationError, match="Unsupported file format"):
            self.framework.parse_resume(txt_file)
    
    def test_nonexistent_file(self):
        """Test that nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            self.framework.parse_resume("nonexistent_file.pdf")
    
    def test_register_parser(self):
        """Test registering a custom parser."""
        class CustomParser(FileParser):
            def parse(self, file_path):
                return "Custom parsed text"
        
        # Register parser
        ResumeParserFramework.register_parser(".custom", CustomParser)
        
        # Verify it's registered
        assert ".custom" in ResumeParserFramework.PARSER_REGISTRY
        assert ResumeParserFramework.PARSER_REGISTRY[".custom"] == CustomParser
    
    def test_register_parser_without_dot(self):
        """Test that parser registration works without leading dot."""
        class AnotherParser(FileParser):
            def parse(self, file_path):
                return "Another parsed text"
        
        # Register without dot
        ResumeParserFramework.register_parser("another", AnotherParser)
        
        # Should be registered with dot
        assert ".another" in ResumeParserFramework.PARSER_REGISTRY

