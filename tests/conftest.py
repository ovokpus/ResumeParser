"""Pytest fixtures and configuration."""

import warnings
import pytest
from pathlib import Path

# Suppress PyMuPDF C binding warnings (not actionable - from underlying C library)
# These must be filtered before PyMuPDF is imported
warnings.filterwarnings("ignore", message=".*SwigPyPacked.*", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*SwigPyObject.*", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*swigvarlink.*", category=DeprecationWarning)

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

