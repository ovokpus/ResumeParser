# Testing with Real Resume Documents

This guide shows you how to test the Resume Parser Framework with actual resume files.

## Quick Start

### Option 1: Component-by-Component Testing (Recommended)

This approach works even without the SpaCy model installed:

```python
from resume_parser.parsers.pdf_parser import PDFParser
from resume_parser.extractors.email_extractor import EmailExtractor
from resume_parser.extractors.skills_extractor import SkillsExtractor
from resume_parser.models import ResumeData

# 1. Parse PDF to text
parser = PDFParser()
text = parser.parse("path/to/resume.pdf")
print(f"Extracted {len(text)} characters")

# 2. Extract email
email_extractor = EmailExtractor()
email = email_extractor.extract(text)
print(f"Email: {email}")

# 3. Extract skills (requires OpenAI API key)
skills_extractor = SkillsExtractor()
skills = skills_extractor.extract(text)
print(f"Skills: {skills}")

# 4. Create structured output
result = ResumeData(
    name="John Doe",  # Manual for now, or use SpaCy
    email=email,
    skills=skills
)
print(result.to_dict())
```

### Option 2: Full Framework (Requires SpaCy Model)

Once SpaCy model is installed:

```python
from resume_parser import ResumeParserFramework

framework = ResumeParserFramework()
result = framework.parse_resume("path/to/resume.pdf")

print(f"Name: {result.name}")
print(f"Email: {result.email}")
print(f"Skills: {result.skills}")
```

## Where to Get Test Resumes

### 1. Create Your Own

**Simple Text Resume** (save as PDF using Google Docs or Word):

```
JANE SMITH
Senior Software Engineer

Email: jane.smith@email.com
Phone: (555) 987-6543
LinkedIn: linkedin.com/in/janesmith

PROFESSIONAL SUMMARY
Experienced software engineer with 8+ years building scalable web applications.
Expertise in Python, cloud infrastructure, and team leadership.

TECHNICAL SKILLS
• Languages: Python, JavaScript, TypeScript, SQL
• Frameworks: Django, FastAPI, React, Next.js
• Cloud & DevOps: AWS, Docker, Kubernetes, Terraform
• Databases: PostgreSQL, MongoDB, Redis
• Tools: Git, CI/CD, Agile/Scrum

PROFESSIONAL EXPERIENCE

Senior Software Engineer | TechCorp Inc. | 2020 - Present
• Architected and deployed microservices handling 1M+ requests/day
• Led team of 6 engineers in agile development
• Reduced infrastructure costs by 40% through AWS optimization
• Technologies: Python, AWS, Docker, PostgreSQL

Software Engineer | StartupXYZ | 2017 - 2020
• Built RESTful APIs serving mobile and web applications
• Implemented CI/CD pipelines reducing deployment time by 60%
• Technologies: Django, React, MongoDB

EDUCATION
Bachelor of Science in Computer Science
University of Technology | 2017
```

### 2. Download Sample Resumes

**Free Sample Resume Sites:**
- [Resume.com Templates](https://www.resume.com/)
- [Canva Resume Templates](https://www.canva.com/resumes/templates/)
- [Google Docs Resume Templates](https://docs.google.com/document/u/0/?tgif=d&ftv=1)

**GitHub Sample Resumes:**
```bash
# Search for sample resumes
git clone https://github.com/sb2nov/resume
# Or search: "sample resume PDF site:github.com"
```

### 3. Convert Existing Resume

If you have a Word resume:
- Open in Microsoft Word
- File → Save As → PDF

If you have a text file:
- Copy to Google Docs
- File → Download → PDF

## Running the Tests

### Automated Test Script

```bash
# Run the test script
.venv/bin/python test_real_resume.py
```

The script will:
1. Check if test resume exists
2. Parse the PDF/Word file
3. Extract email (always works)
4. Extract skills (needs OpenAI API key)
5. Show results

### Manual Testing in Python REPL

```bash
# Start Python
.venv/bin/python

# Then run:
```

```python
from resume_parser.parsers.pdf_parser import PDFParser
from resume_parser.extractors.email_extractor import EmailExtractor

# Parse a PDF
parser = PDFParser()
text = parser.parse("my_resume.pdf")

# See the extracted text
print(text[:500])  # First 500 characters

# Extract email
email_extractor = EmailExtractor()
email = email_extractor.extract(text)
print(f"Email found: {email}")
```

## Expected Output

For a typical resume, you should see:

```json
{
  "name": "Jane Smith",
  "email": "jane.smith@email.com",
  "skills": [
    "Python",
    "JavaScript",
    "TypeScript",
    "Django",
    "FastAPI",
    "React",
    "Next.js",
    "AWS",
    "Docker",
    "Kubernetes",
    "PostgreSQL",
    "MongoDB",
    "Redis",
    "Git",
    "CI/CD",
    "Agile",
    "Team Leadership",
    "System Architecture"
  ]
}
```

## Troubleshooting

### PDF is Image-Based

**Problem**: PDF returns empty or garbled text

**Solution**: The PDF might be scanned/image-based. You need OCR:
```python
# This framework doesn't include OCR
# Use pytesseract or AWS Textract for image-based PDFs
```

### No Email Found

**Problem**: Email extractor returns empty string

**Check**:
1. Is there actually an email in the resume?
2. Is it in a standard format? (user@domain.com)
3. Check the raw text: `print(text)` to see what was extracted

### Skills Extraction Fails

**Problem**: SkillsExtractor raises error

**Common causes**:
1. **No API key**: Add `OPENAI_API_KEY` to `.env` file
2. **Invalid API key**: Check the key is correct
3. **Rate limit**: Wait a moment and try again
4. **No internet**: Check connection

### Word Document Won't Parse

**Problem**: `.docx` file fails to parse

**Solution**:
```python
# Make sure it's a .docx file (not .doc)
from resume_parser.parsers.word_parser import WordParser

parser = WordParser()
text = parser.parse("resume.docx")
```

## Performance Tips

### Batch Processing

To process multiple resumes:

```python
from pathlib import Path
from resume_parser.parsers.pdf_parser import PDFParser
from resume_parser.extractors.email_extractor import EmailExtractor

parser = PDFParser()
email_extractor = EmailExtractor()

resume_folder = Path("resumes/")
results = []

for resume_file in resume_folder.glob("*.pdf"):
    try:
        text = parser.parse(resume_file)
        email = email_extractor.extract(text)
        results.append({
            "file": resume_file.name,
            "email": email,
            "status": "success"
        })
    except Exception as e:
        results.append({
            "file": resume_file.name,
            "error": str(e),
            "status": "failed"
        })

# Save results
import json
with open("parsed_resumes.json", "w") as f:
    json.dump(results, f, indent=2)
```

### API Cost Management

Skills extraction uses GPT-4 which costs money:

- **Cost per resume**: ~$0.005-$0.01 (less than a penny)
- **Monitor usage**: Check logs for token counts
- **Optimize**: Only extract skills when needed

```python
# Check token usage in logs
# Look for: "Token usage - Prompt: X, Completion: Y, Total: Z"
```

## Next Steps

1. **Get a resume file** (create or download)
2. **Place it in the project** (e.g., `tests/test_data/`)
3. **Run the test script**: `.venv/bin/python test_real_resume.py`
4. **Check the output** and adjust as needed

Happy parsing! 🚀

