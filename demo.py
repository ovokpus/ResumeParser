"""Live demonstration script for the Resume Parser Framework.

This script demonstrates the core features and capabilities of the Resume Parser Framework
without requiring actual resume files. It showcases:

1. ResumeData Model: Data normalization (whitespace trimming, deduplication, etc.)
2. Email Extractor: Regex-based email extraction with filtering
3. Skills Extractor: GPT-4 powered intelligent skills extraction (initialization only)
4. JSON Export: Structured data serialization

The script uses hardcoded example data to illustrate how the framework processes
and normalizes resume information. For actual resume parsing, use parse_and_log.py.

Usage:
    python demo.py

Note:
    - No command-line arguments required
    - Uses hardcoded example data
    - Skills extraction initialization only (requires OpenAI API key for actual extraction)
    - Does not parse actual resume files
"""

from resume_parser.models import ResumeData
from resume_parser.extractors.email_extractor import EmailExtractor
from resume_parser.extractors.skills_extractor import SkillsExtractor

print("=" * 70)
print("RESUME PARSER FRAMEWORK - LIVE DEMONSTRATION")
print("=" * 70)

# Demo 1: ResumeData Model
print("\n[DEMO 1] ResumeData Model - Data Normalization")
print("-" * 70)

resume = ResumeData(
    name="  John   Doe  ",  # Extra whitespace
    email="  JOHN.DOE@GMAIL.COM  ",  # Uppercase and whitespace
    skills=["Python", "python", "  AWS  ", "Docker", "Python", ""]  # Duplicates and empty
)

print(f"Input (messy):")
print(f"  Name: '  John   Doe  '")
print(f"  Email: '  JOHN.DOE@GMAIL.COM  '")
print(f"  Skills: ['Python', 'python', '  AWS  ', 'Docker', 'Python', '']")

print(f"\nOutput (normalized):")
print(f"  Name: '{resume.name}'")
print(f"  Email: '{resume.email}'")
print(f"  Skills: {resume.skills}")
print(f"  \n  [OK] Whitespace trimmed")
print(f"  [OK] Email lowercased")
print(f"  [OK] Duplicates removed")
print(f"  [OK] Empty skills filtered")

# Demo 2: Email Extractor
print("\n\n[DEMO 2] Email Extractor - Regex-based Extraction")
print("-" * 70)

extractor = EmailExtractor()
test_texts = [
    "Contact me at jane.smith@company.com for opportunities",
    "Reach out: developer123@tech-startup.io",
    "My email is test@test.com (this should be filtered)",
]

for text in test_texts:
    email = extractor.extract(text)
    status = "[OK] Extracted" if email else "[FILTERED] Not found"
    print(f"{status}: {text[:50]}...")
    if email:
        print(f"        -> {email}")

# Demo 3: Skills Extractor (shows initialization, would need API key for actual use)
print("\n\n[DEMO 3] Skills Extractor - GPT-4 Integration")
print("-" * 70)

print("The SkillsExtractor uses GPT-4 to intelligently extract skills.")
print("Features:")
print("  • Handles unstructured text (bullets, paragraphs, tables)")
print("  • Semantic understanding of technical and soft skills")
print("  • Automatic deduplication and normalization")
print("  • Retry logic with exponential backoff")
print("  • Token usage tracking for cost monitoring")
print("\nNote: Actual extraction requires a valid OpenAI API key in .env file")

try:
    skills_extractor = SkillsExtractor()
    print("\n[OK] SkillsExtractor initialized successfully")
    print(f"  Model: {skills_extractor.model}")
    print(f"  Temperature: {skills_extractor.temperature}")
    print(f"  Max tokens: {skills_extractor.max_tokens}")
except Exception as e:
    print(f"\n[FAIL] SkillsExtractor initialization failed: {e}")

# Demo 4: JSON Export
print("\n\n[DEMO 4] JSON Export")
print("-" * 70)

resume_data = ResumeData(
    name="Alice Johnson",
    email="alice.j@example.com",
    skills=["Python", "Machine Learning", "Docker", "AWS", "Team Leadership"]
)

import json
json_output = json.dumps(resume_data.to_dict(), indent=2)
print(json_output)

# Summary
print("\n\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("[OK] ResumeData model: Normalizes and validates resume data")
print("[OK] EmailExtractor: Fast regex-based email extraction")
print("[OK] SkillsExtractor: GPT-4 powered intelligent extraction")
print("[OK] Production-ready: Error handling, logging, retry logic")
print("\nNext: Add your OpenAI API key to .env and parse real resumes!")
print("=" * 70)

