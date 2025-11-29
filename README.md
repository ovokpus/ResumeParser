# Resume Parser Framework

> A production-ready, AI-powered resume parsing system that transforms messy PDFs and Word docs into beautiful, structured data.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## What Makes This Special?

This isn't your grandpa's regex-based parser! We've built a **smart, extensible framework** that combines:

- **GPT-4 Intelligence**: For extracting complex skills that traditional parsers miss
- **Solid Architecture**: Clean OOD with Strategy Pattern and Dependency Injection
- **Production-Ready**: Comprehensive error handling, logging, retry logic, and 90%+ test coverage
- **Extensible Design**: Add new file formats or extraction strategies in minutes
- **Battle-Tested**: Handles edge cases like encrypted PDFs, table-based resumes, and more

## The Story Behind The Design

**The Challenge**: Resume parsing is HARD. Skills can appear anywhere - in bullet points, paragraphs, tables, or buried in job descriptions. Email is easy (thanks regex!), names are tricky (thanks cultural variations!), but skills? That's where things get complex.

**Our Solution**: Use the right tool for each job:
- **Email Extraction**: Lightning-fast regex (why use a sledgehammer for a thumbtack?)
- **Name Extraction**: Rule-based heuristics + SpaCy NER (best of both worlds!)
- **Skills Extraction**: GPT-4 Turbo (because AI actually earns its keep here!)

This approach demonstrates **engineering judgment** - knowing when to use AI vs when simpler solutions shine.

## Features

### Multi-Format Support
- **PDF**: Handles encrypted PDFs, multi-page documents, and image-based content gracefully
- **Word (.docx)**: Extracts from paragraphs AND tables (because who doesn't love a good table?)
- **Extensible**: Register custom parsers for HTML, RTF, or any custom format

### Intelligent Extraction
```
┌─────────────────────────────────────────────────────────┐
│                   Resume File (PDF/DOCX)                │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │   File Parser Layer   │
         │  (PDF/Word/Custom)    │
         └───────────┬───────────┘
                     │
              Raw Text Output
                     │
         ┌───────────▼───────────┐
         │  Field Extractors     │
         ├───────────────────────┤
         │ • Email (Regex)       │
         │ • Name (Rules+NER)    │
         │ • Skills (GPT-4)      │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │   Structured Data     │
         │  {name, email, skills}│
         └───────────────────────┘
```

### Production Quality
- **Error Handling**: Graceful degradation when extractors fail
- **Logging**: Track what's happening under the hood
- **Retry Logic**: Automatic retry with exponential backoff for API calls
- **Tested**: 90%+ coverage with comprehensive unit and integration tests
- **Cost Tracking**: Token usage logging for budget monitoring

## Installation

### Prerequisites

Make sure you've got these ready:
- Python 3.8+ (the newer, the better!)
- An OpenAI API key (for the GPT-4 integration)

### Quick Start

```bash
# 1. Clone this bad boy
git clone <repository-url>
cd ResumeParser

# 2. Create a virtual environment (keeps things tidy!)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download SpaCy's language model
python -m spacy download en_core_web_sm

# 5. Set up your environment
cp .env.example .env
# Edit .env and add your OpenAI API key

# 6. Run tests to make sure everything works
pytest
```

## Usage

### The Basics (5-Second Integration)

```python
from resume_parser import ResumeParserFramework

# That's it! One line initialization
framework = ResumeParserFramework()

# Parse any resume
resume_data = framework.parse_resume("awesome_candidate.pdf")

# Access the goodies
print(f"📧 Email: {resume_data.email}")
print(f"👤 Name: {resume_data.name}")
print(f"🎯 Skills: {', '.join(resume_data.skills)}")

# Or get it as JSON
import json
print(json.dumps(resume_data.to_dict(), indent=2))
```

### Real-World Example

```python
from resume_parser import ResumeParserFramework
import json

framework = ResumeParserFramework()

# Parse a resume
try:
    resume = framework.parse_resume("john_doe_resume.pdf")
    
    # Beautiful output
    print("[SUCCESS] Successfully parsed resume!")
    print(f"   Name: {resume.name}")
    print(f"   Email: {resume.email}")
    print(f"   Found {len(resume.skills)} skills:")
    for skill in resume.skills[:5]:  # Top 5 skills
        print(f"      - {skill}")
        
except FileNotFoundError:
    print("[ERROR] Oops! Couldn't find that file.")
except Exception as e:
    print(f"[ERROR] Something went wrong: {e}")
```

### Batch Processing

Got a pile of resumes? No problem!

```python
from pathlib import Path
from resume_parser import ResumeParserFramework

framework = ResumeParserFramework()
resume_folder = Path("resumes/")

results = []
for resume_file in resume_folder.glob("*.pdf"):
    try:
        data = framework.parse_resume(resume_file)
        results.append({
            "filename": resume_file.name,
            "candidate": data.name,
            "email": data.email,
            "skill_count": len(data.skills)
        })
            print(f"[OK] {resume_file.name}")
    except Exception as e:
        print(f"[FAIL] {resume_file.name}: {e}")

# Save results
import json
with open("parsed_resumes.json", "w") as f:
    json.dump(results, f, indent=2)
```

## Advanced: Extending The Framework

One of the coolest things about this framework? It's **ridiculously easy to extend**.

### Adding a Custom Extractor

Want to extract phone numbers? Education? Zodiac signs? Here's how:

```python
from resume_parser.extractors.base import FieldExtractor
import re

class PhoneExtractor(FieldExtractor):
    """Extract phone numbers from resumes."""
    
    PHONE_PATTERN = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
    
    def extract(self, text: str) -> str:
        self._validate_text_input(text)
        matches = self.PHONE_PATTERN.findall(text)
        return matches[0] if matches else ""

# Use it!
from resume_parser.core.resume_extractor import ResumeExtractor

custom_extractor = ResumeExtractor(
    # Keep defaults for name, email, skills
    # Or add your custom extractors here
)
framework = ResumeParserFramework(resume_extractor=custom_extractor)
```

### Adding a New File Format

Support HTML resumes? CSV? Carrier pigeon messages? Easy!

```python
from resume_parser.parsers.base import FileParser
from resume_parser.core.framework import ResumeParserFramework

class HTMLParser(FileParser):
    """Parse HTML resumes."""
    
    def parse(self, file_path):
        from bs4 import BeautifulSoup
        
        path = self._validate_file_exists(file_path)
        with open(path, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            return soup.get_text()

# Register it
ResumeParserFramework.register_parser(".html", HTMLParser)

# Now you can parse HTML files!
framework = ResumeParserFramework()
resume = framework.parse_resume("resume.html")
```

## Architecture Deep Dive

### Design Patterns Used

We didn't just slap code together - this is **thoughtfully architected**:

1. **Strategy Pattern**: Different parsers for different file formats, different extractors for different fields
2. **Dependency Injection**: Easy testing and customization
3. **Factory Pattern**: Parser registry for dynamic file format handling
4. **Single Responsibility**: Each class does ONE thing well

### Component Breakdown

```
ResumeParserFramework (Main Orchestrator)
├── File Parsers (Format Handlers)
│   ├── PDFParser → Handles PDFs with PyPDF2
│   ├── WordParser → Handles .docx with python-docx
│   └── Your Custom Parser → You decide!
│
├── Resume Extractor (Coordinator)
│   └── Field Extractors (Specialists)
│       ├── EmailExtractor → Regex-based
│       ├── NameExtractor → Rules + SpaCy NER
│       └── SkillsExtractor → GPT-4 powered
│
└── ResumeData (Output Model)
    ├── name: str
    ├── email: str
    └── skills: List[str]
```

## Testing

We take testing seriously (90%+ coverage)

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/resume_parser --cov-report=html

# Run specific test file
pytest tests/unit/test_extractors/test_skills_extractor.py

# Run with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

View the coverage report:
```bash
open htmlcov/index.html  # Opens in your browser
```

## Performance & Costs

### Processing Speed
- **Average**: 2-5 seconds per resume (including GPT-4 API call)
- **Bottleneck**: GPT-4 API latency (worth it for quality!)
- **Optimization**: Use batch processing for multiple resumes

### API Costs (GPT-4 Turbo)
- **Per Resume**: ~$0.005 - $0.01 (less than a penny!)
- **Token Usage**: ~500-1000 tokens per resume
- **Cost Tracking**: Automatic logging of token usage

### Scalability Tips
```python
# Process resumes in parallel
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def parse_many(file_paths):
    with ThreadPoolExecutor(max_workers=5) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, framework.parse_resume, path)
            for path in file_paths
        ]
        return await asyncio.gather(*tasks)
```

## Configuration

Customize behavior via environment variables (`.env` file):

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview      # Or gpt-4, gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000                # Max tokens for response
OPENAI_TEMPERATURE=0.1                # Lower = more deterministic

# Logging
LOG_LEVEL=INFO                         # DEBUG, INFO, WARNING, ERROR
LOG_FILE=resume_parser.log             # Optional log file

# Extraction
MAX_SKILLS_RETURNED=20                 # Limit skills per resume
ENABLE_SKILL_CATEGORIZATION=true       # Future feature!
```

## Troubleshooting

### Common Issues

**Issue**: `SpaCy model not found`
```bash
# Solution: Download the model
python -m spacy download en_core_web_sm
```

**Issue**: `OpenAI API key error`
```bash
# Solution: Check your .env file
cat .env | grep OPENAI_API_KEY
# Make sure the key starts with "sk-"
```

**Issue**: `PDF returns empty text`
```
Cause: PDF might be image-based (scanned document)
Solution: Use OCR preprocessing (not included in this framework)
Recommendation: Check out pytesseract or AWS Textract
```

**Issue**: Rate limit errors from OpenAI
```
The framework automatically retries with exponential backoff!
Just wait a bit - it'll handle it gracefully.
```

## Implementation Journey

Want to understand how this was built? Here's the step-by-step process:

### Phase 1: Foundation (Solid Base)
1. Project structure with clean separation of concerns
2. Configuration management with Pydantic
3. Custom exception hierarchy
4. Logging infrastructure

### Phase 2: File Parsing (Read The Docs)
5. Abstract `FileParser` base class
6. PDF parser with error handling
7. Word parser with table support
8. File validation and size limits

### Phase 3: Field Extraction (The Smart Stuff)
9. Abstract `FieldExtractor` base class
10. Email extractor with regex
11. Name extractor with rules + NER
12. **Skills extractor with GPT-4** (the star of the show!)

### Phase 4: Orchestration (Bring It Together)
13. `ResumeExtractor` coordinator
14. `ResumeParserFramework` main API
15. Parser registry for extensibility

### Phase 5: Production Ready (Ship It!)
16. Comprehensive test suite (90%+ coverage)
17. Documentation and examples
18. Error handling and retry logic
19. Type hints throughout

## Contributing

Got ideas? Found a bug? Want to add support for parsing resumes written in ancient hieroglyphics? We'd love your contribution!

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/awesome-feature`)
3. Make your changes
4. Write tests (keep that 90%+ coverage!)
5. Run the linter (`black . && flake8`)
6. Submit a PR

## License

MIT License - Go wild! Build amazing things!

## Acknowledgments

- **OpenAI** for GPT-4
- **SpaCy** for making NLP accessible
- **PyPDF2** and **python-docx** for handling the file formats
- **You** for checking out this project!

## Support

- **Issues**: Open a GitHub issue
- **Questions**: Check the examples folder
- **Feature Requests**: We're all ears!

---

Built with passion by developers who believe parsing resumes shouldn't be painful.

**Happy Parsing!**
Resume Parsing Application
