"""Unit tests for ResumeData model."""

import pytest
from resume_parser.models import ResumeData


class TestResumeData:
    """Test suite for ResumeData model."""
    
    def test_create_resume_data(self):
        """Test creating ResumeData instance."""
        data = ResumeData(
            name="John Doe",
            email="john@example.com",
            skills=["Python", "AWS"]
        )
        
        assert data.name == "John Doe"
        assert data.email == "john@example.com"
        assert data.skills == ["Python", "AWS"]
    
    def test_name_normalization(self):
        """Test that extra whitespace is removed from names."""
        data = ResumeData(
            name="  John   Doe  ",
            email="john@example.com",
            skills=[]
        )
        
        assert data.name == "John Doe"
    
    def test_email_normalization(self):
        """Test that email is lowercased and trimmed."""
        data = ResumeData(
            name="John Doe",
            email="  John.Doe@EXAMPLE.COM  ",
            skills=[]
        )
        
        assert data.email == "john.doe@example.com"
    
    def test_skills_deduplication(self):
        """Test that duplicate skills are removed."""
        data = ResumeData(
            name="John Doe",
            email="john@example.com",
            skills=["Python", "python", "AWS", "Python"]
        )
        
        # Should keep only one "Python" (case-insensitive)
        assert len(data.skills) == 2
        assert "Python" in data.skills
        assert "AWS" in data.skills
    
    def test_skills_empty_string_removal(self):
        """Test that empty strings are removed from skills."""
        data = ResumeData(
            name="John Doe",
            email="john@example.com",
            skills=["Python", "", "  ", "AWS"]
        )
        
        assert len(data.skills) == 2
        assert "" not in data.skills
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        data = ResumeData(
            name="John Doe",
            email="john@example.com",
            skills=["Python", "AWS"]
        )
        
        result = data.to_dict()
        
        assert isinstance(result, dict)
        assert result["name"] == "John Doe"
        assert result["email"] == "john@example.com"
        assert result["skills"] == ["Python", "AWS"]
    
    def test_default_empty_skills(self):
        """Test that skills defaults to empty list."""
        data = ResumeData(
            name="John Doe",
            email="john@example.com"
        )
        
        assert data.skills == []

