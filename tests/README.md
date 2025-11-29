# Test Suite Documentation

This directory contains the comprehensive test suite for the Resume Parser Framework.

## Overview

- **Total Tests**: 53 tests
- **Unit Tests**: 28 tests
- **Integration Tests**: 25 tests
- **Test Coverage**: 90%+

**Note:** The test suite validates the framework's Object-Oriented Design (OOD) architecture. For detailed OOD documentation including class hierarchy, design patterns, and how tests validate OOD principles, see **[docs/object-oriented-design.md](../docs/object-oriented-design.md)**.

## Test Organization

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── unit/                          # Unit tests (28 tests)
│   ├── test_models.py            # ResumeData model tests
│   ├── test_core/                # Core framework tests
│   │   └── test_framework.py
│   ├── test_extractors/          # Field extractor tests
│   │   ├── test_email_extractor.py
│   │   └── test_skills_extractor.py
│   └── test_parsers/             # File parser tests
└── integration/                   # Integration tests (25 tests)
    ├── test_setup_verification.py
    ├── test_openai_connectivity.py
    ├── test_real_resume_parsing.py
    └── test_comprehensive_resume_parsing.py
```

## Running Tests

### Run All Tests

```bash
# Using uv
uv run pytest

# Using pytest directly
pytest
```

### Run Specific Test Categories

**Unit Tests Only:**
```bash
uv run pytest tests/unit/ -v
```

**Integration Tests Only:**
```bash
uv run pytest tests/integration/ -v
```

**Specific Test File:**
```bash
uv run pytest tests/unit/test_models.py -v
uv run pytest tests/integration/test_setup_verification.py -v
```

**Specific Test Class:**
```bash
uv run pytest tests/unit/test_extractors/test_email_extractor.py::TestEmailExtractor -v
```

**Specific Test Function:**
```bash
uv run pytest tests/unit/test_models.py::test_create_resume_data -v
```

### Run Tests with Coverage

```bash
# Generate coverage report
uv run pytest --cov=src/resume_parser --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run Tests with Markers

```bash
# Run only slow tests (if marked)
uv run pytest -m slow

# Run tests excluding integration (if marked)
uv run pytest -m "not integration"
```


## Test Categories

### Unit Tests (28 tests)

#### 1. ResumeData Model Tests (`test_models.py`) - 7 tests

Tests the core data model for resume information:

- `test_create_resume_data` - Basic model creation
- `test_name_normalization` - Whitespace trimming in names
- `test_email_normalization` - Lowercase email conversion
- `test_skills_deduplication` - Removes duplicate skills (case-insensitive)
- `test_skills_empty_string_removal` - Filters out empty strings
- `test_to_dict` - JSON serialization
- `test_default_empty_skills` - Default empty list for skills

**Run:**
```bash
uv run pytest tests/unit/test_models.py -v
```

#### 2. Framework Tests (`test_core/test_framework.py`) - 5 tests

Tests the main ResumeParserFramework class:

- `test_initialization` - Framework initialization
- `test_unsupported_file_format` - Error handling for unsupported formats
- `test_nonexistent_file` - FileNotFoundError handling
- `test_register_parser` - Parser registration functionality
- `test_register_parser_without_dot` - Parser registration edge cases

**Run:**
```bash
uv run pytest tests/unit/test_core/test_framework.py -v
```

#### 3. Email Extractor Tests (`test_extractors/test_email_extractor.py`) - 9 tests

Tests regex-based email extraction:

- `test_extract_simple_email` - Basic email extraction
- `test_extract_email_with_numbers` - Email with numbers (e.g., john123@example.com)
- `test_extract_email_with_plus` - Email with plus sign (e.g., john+tag@example.com)
- `test_extract_first_email_when_multiple` - Multiple emails (returns first)
- `test_no_email_found` - No email in text
- `test_invalid_email_filtered` - Filters test@test.com and similar
- `test_empty_text_raises_error` - Empty input validation
- `test_whitespace_only_raises_error` - Whitespace-only input validation
- `test_email_in_complex_resume` - Email extraction from complex text

**Run:**
```bash
uv run pytest tests/unit/test_extractors/test_email_extractor.py -v
```

#### 4. Skills Extractor Tests (`test_extractors/test_skills_extractor.py`) - 7 tests

Tests GPT-4 powered skills extraction:

- `test_extract_skills_success` - Successful skills extraction
- `test_extract_skills_empty_result` - Empty response handling
- `test_extract_skills_filters_empty_strings` - Filters empty strings from results
- `test_extract_skills_limits_max_skills` - Respects MAX_SKILLS_RETURNED limit
- `test_extract_skills_invalid_json` - Invalid JSON response handling
- `test_extract_skills_truncates_long_text` - Text truncation for API limits
- `test_empty_text_raises_error` - Empty input validation

**Note:** These tests use mocking to avoid actual API calls during testing.

**Run:**
```bash
uv run pytest tests/unit/test_extractors/test_skills_extractor.py -v
```

### Integration Tests (25 tests)

#### 1. Setup Verification Tests (`test_setup_verification.py`) - 5 tests

Verifies the framework is properly set up:

- `test_imports` - All modules import successfully
- `test_environment_variables` - Environment variables are accessible
- `test_spacy_model` - SpaCy model loads correctly
- `test_resume_data_model` - ResumeData model works
- `test_framework_initialization` - Framework initializes without errors

**Run:**
```bash
uv run pytest tests/integration/test_setup_verification.py -v
```

#### 2. OpenAI Connectivity Tests (`test_openai_connectivity.py`) - 3 tests

Tests OpenAI API connectivity (requires valid API key):

- `test_openai_api_key_set` - API key is configured
- `test_openai_api_key_format` - API key format is valid (starts with 'sk-')
- `test_openai_connectivity` - Can actually connect to OpenAI API

**Note:** Tests are skipped if API key is not set or is a placeholder.

**Run:**
```bash
uv run pytest tests/integration/test_openai_connectivity.py -v
```

#### 3. Real Resume Parsing Tests (`test_real_resume_parsing.py`) - 4 tests

Tests parsing of actual resume files:

- `test_pdf_parsing_component` - PDF parsing to text
- `test_email_extraction_from_resume` - Email extraction from real resume
- `test_skills_extraction_from_resume` - Skills extraction (requires API key)
- `test_full_framework_parsing` - End-to-end parsing workflow

**Run:**
```bash
uv run pytest tests/integration/test_real_resume_parsing.py -v
```

#### 4. Comprehensive Resume Parsing Tests (`test_comprehensive_resume_parsing.py`) - 13 tests

Comprehensive tests covering various resume types and edge cases:

**File Format Tests:**
- `test_all_pdf_files_parseable` - All PDF files in test_data can be parsed
- `test_all_docx_files_parseable` - All DOCX files in test_data can be parsed

**Resume Type Tests:**
- `test_specific_resume_types[software_engineer_resume]` - Software engineer resumes
- `test_specific_resume_types[data_scientist_resume]` - Data scientist resumes
- `test_specific_resume_types[multi_page_resume]` - Multi-page resumes
- `test_specific_resume_types[resume_with_tables]` - Resumes with tables

**Full Parsing Tests:**
- `test_software_engineer_resumes_full_parsing` - Complete parsing of SE resumes
- `test_data_scientist_resumes_full_parsing` - Complete parsing of DS resumes
- `test_multi_page_resume` - Multi-page document handling
- `test_resume_with_tables` - Table extraction from DOCX

**Edge Case Tests:**
- `test_edge_cases_minimal_resume` - Minimal content resumes
- `test_edge_cases_encrypted_resume` - Encrypted PDFs (should fail gracefully)
- `test_edge_cases_corrupted_resume` - Corrupted files (should fail gracefully)

**Run:**
```bash
# All comprehensive tests
uv run pytest tests/integration/test_comprehensive_resume_parsing.py -v

# Only edge case tests
uv run pytest tests/integration/test_comprehensive_resume_parsing.py -k "edge_case" -v

# Only file format tests
uv run pytest tests/integration/test_comprehensive_resume_parsing.py -k "parseable" -v
```

## Test Data

Test resumes are located in `tests/test_data/`:

**Standard Resumes:**
- `sample_resume.pdf` / `sample_resume.docx` - Basic sample resume
- `software_engineer_resume.pdf` / `software_engineer_resume.docx` - SE resume
- `software_engineer_resume-2.pdf` - Additional SE resume
- `data_scientist_resume.pdf` / `data_scientist_resume.docx` - DS resume
- `multi_page_resume.pdf` / `multi_page_resume.docx` - Multi-page resume
- `resume_with_tables.pdf` / `resume_with_tables.docx` - Resume with tables

**Edge Cases:**
- `edge_cases/minimal_resume.pdf` - Minimal content (should parse successfully)
- `edge_cases/encrypted_resume.pdf` - Password-protected (should fail gracefully)
- `edge_cases/corrupted_resume.pdf` - Corrupted file (should fail gracefully)

## Test Fixtures

Shared fixtures are defined in `conftest.py`:

- `sample_resume_text` - Sample resume text for testing
- `sample_resume_data` - Sample ResumeData object
- `test_data_dir` - Path to test data directory
- `mock_openai_response` - Mock OpenAI API response

**Usage:**
```python
def test_something(sample_resume_text, test_data_dir):
    # Use fixtures in your tests
    text = sample_resume_text
    resume_path = test_data_dir / "sample_resume.pdf"
```

## Writing New Tests

### Unit Test Example

```python
import pytest
from resume_parser.models import ResumeData

def test_new_feature():
    """Test description."""
    # Arrange
    data = ResumeData(name="Test", email="test@example.com", skills=[])
    
    # Act
    result = data.to_dict()
    
    # Assert
    assert result["name"] == "Test"
    assert result["email"] == "test@example.com"
```

### Integration Test Example

```python
import pytest
from resume_parser import ResumeParserFramework

def test_parse_real_resume(test_data_dir):
    """Test parsing a real resume file."""
    framework = ResumeParserFramework()
    resume_path = test_data_dir / "sample_resume.pdf"
    
    result = framework.parse_resume(str(resume_path))
    
    assert result.name is not None
    assert result.email is not None
```

## Test Best Practices

1. **Use Descriptive Names**: Test names should clearly describe what they test
2. **AAA Pattern**: Arrange, Act, Assert structure
3. **One Assertion Per Concept**: Test one thing per test function
4. **Use Fixtures**: Reuse common test data via fixtures
5. **Mock External Services**: Mock API calls and file I/O when possible
6. **Test Edge Cases**: Include tests for error conditions and boundary cases
7. **Keep Tests Fast**: Unit tests should be fast (< 1 second)
8. **Isolation**: Tests should not depend on each other

## Common Test Commands

```bash
# Run all tests with verbose output
uv run pytest -v

# Run tests and show print statements
uv run pytest -v -s

# Run tests and stop on first failure
uv run pytest -x

# Run tests matching a pattern
uv run pytest -k "email" -v

# Run tests with coverage
uv run pytest --cov=src/resume_parser --cov-report=term-missing

# Run tests in parallel (if pytest-xdist installed)
uv run pytest -n auto
```

## Troubleshooting Tests

### Tests Fail Due to Missing API Key

Some tests require a valid OpenAI API key. If you don't have one:
- Tests will be skipped automatically
- Or set a placeholder key: `export OPENAI_API_KEY=sk-placeholder`

### Tests Fail Due to Missing SpaCy Model

```bash
# Download the model
uv run python -m spacy download en_core_web_sm
```

### Tests Fail Due to Import Errors

```bash
# Make sure you're in the project root
cd /path/to/ResumeParser

# Install dependencies
uv sync
# OR
pip install -r requirements.txt
```

### Tests Are Slow

- Unit tests should be fast (< 1 second total)
- Integration tests may be slower due to file I/O and API calls
- Use `-k` to run specific tests instead of all tests

## Test Coverage Goals

- **Overall Coverage**: 90%+
- **Critical Paths**: 100% coverage
- **Edge Cases**: All edge cases tested
- **Error Handling**: All error paths tested

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    uv sync
    uv run pytest --cov=src/resume_parser --cov-report=xml
```

---

**For more information, see the main [README.md](../README.md)**

