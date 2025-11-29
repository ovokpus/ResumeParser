"""Quick test script to verify the resume parser framework setup."""

import os
from pathlib import Path

print("Testing Resume Parser Framework Setup")
print("=" * 60)

# Test 1: Check if we can import the framework
print("\n1. Testing imports...")
try:
    from resume_parser import ResumeParserFramework, ResumeData
    print("   ✓ Successfully imported ResumeParserFramework")
    print("   ✓ Successfully imported ResumeData")
except ImportError as e:
    print(f"   ✗ Import error: {e}")
    exit(1)

# Test 2: Check environment variables
print("\n2. Checking environment variables...")
if not os.getenv('OPENAI_API_KEY'):
    print("   ⚠ WARNING: OPENAI_API_KEY not set in environment")
    print("   → You need to add your OpenAI API key to .env file")
else:
    api_key = os.getenv('OPENAI_API_KEY')
    masked_key = f"{api_key[:7]}...{api_key[-4:]}" if len(api_key) > 11 else "***"
    print(f"   ✓ OPENAI_API_KEY is set: {masked_key}")

# Test 3: Check SpaCy model
print("\n3. Checking SpaCy model...")
try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
        print("   ✓ SpaCy model 'en_core_web_sm' is installed")
    except OSError:
        print("   ✗ SpaCy model 'en_core_web_sm' not found")
        print("   → Run: uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl")
except ImportError:
    print("   ✗ SpaCy not installed")

# Test 4: Create a simple ResumeData object
print("\n4. Testing ResumeData model...")
try:
    resume_data = ResumeData(
        name="John Doe",
        email="john.doe@example.com",
        skills=["Python", "AWS", "Docker"]
    )
    print(f"   ✓ Created ResumeData: {resume_data.to_dict()}")
except Exception as e:
    print(f"   ✗ Error creating ResumeData: {e}")

# Test 5: Initialize framework (without actually parsing)
print("\n5. Testing framework initialization...")
try:
    framework = ResumeParserFramework()
    print("   ✓ Framework initialized successfully")
except Exception as e:
    print(f"   ✗ Error initializing framework: {e}")

print("\n" + "=" * 60)
print("Setup verification complete!")
print("\nNext steps:")
print("1. Add your OpenAI API key to .env file if not done")
print("2. Install SpaCy model if not done:")
print("   uv pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl")
print("3. Create a test resume (PDF or DOCX)")
print("4. Test parsing with: framework.parse_resume('path/to/resume.pdf')")

