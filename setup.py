"""Setup script for Resume Parser Framework."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="resume-parser-framework",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A production-ready, AI-powered resume parsing framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/resume-parser-framework",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyPDF2>=3.0.1",
        "python-docx>=1.1.0",
        "spacy>=3.7.2",
        "openai>=1.6.1",
        "tiktoken>=0.5.2",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.3",
        "pydantic-settings>=2.1.0",
        "tenacity>=8.2.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "responses>=0.24.1",
            "black>=23.12.1",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "isort>=5.13.2",
            "ipython>=8.19.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "resume-parser=resume_parser.cli:main",  # Future CLI support
        ],
    },
)

