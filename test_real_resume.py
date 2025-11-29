"""Test the Resume Parser with real resume documents."""

import sys
from pathlib import Path
from resume_parser import ResumeParserFramework
from resume_parser.extractors.email_extractor import EmailExtractor
from resume_parser.extractors.skills_extractor import SkillsExtractor
from resume_parser.models import ResumeData

print("=" * 70)
print("TESTING WITH REAL RESUME DOCUMENTS")
print("=" * 70)

# Initialize framework
print("\n[Step 1] Initializing framework...")
try:
    framework = ResumeParserFramework()
    print("✓ Framework initialized successfully")
except Exception as e:
    print(f"✗ Framework initialization failed: {e}")
    print("\nNote: Name extraction requires SpaCy model.")
    print("For now, we can test email and skills extraction separately.\n")

# Check for test resume file
test_resume_path = "tests/test_data/sample_resume.pdf"
print(f"\n[Step 2] Looking for test resume at: {test_resume_path}")

if not Path(test_resume_path).exists():
    print(f"✗ Test resume not found at {test_resume_path}")
    print("\n" + "=" * 70)
    print("HOW TO TEST WITH REAL DOCUMENTS")
    print("=" * 70)
    print("""
1. CREATE OR GET A RESUME FILE:
   - PDF format (.pdf) or Word format (.docx)
   - Place it in: tests/test_data/sample_resume.pdf
   
2. OPTION A - Test Full Parsing (requires SpaCy model):
   ```python
   from resume_parser import ResumeParserFramework
   
   framework = ResumeParserFramework()
   result = framework.parse_resume("path/to/resume.pdf")
   
   print(f"Name: {result.name}")
   print(f"Email: {result.email}")
   print(f"Skills: {result.skills}")
   ```

3. OPTION B - Test Components Separately (works without SpaCy):
   ```python
   from resume_parser.parsers.pdf_parser import PDFParser
   from resume_parser.extractors.email_extractor import EmailExtractor
   from resume_parser.extractors.skills_extractor import SkillsExtractor
   
   # Parse PDF to text
   parser = PDFParser()
   text = parser.parse("path/to/resume.pdf")
   
   # Extract email
   email_extractor = EmailExtractor()
   email = email_extractor.extract(text)
   print(f"Email: {email}")
   
   # Extract skills (requires OpenAI API key in .env)
   skills_extractor = SkillsExtractor()
   skills = skills_extractor.extract(text)
   print(f"Skills: {skills}")
   ```

4. CREATE A SAMPLE RESUME:
   You can create a simple text file and save as PDF, or use this text:
   
   ---
   JOHN DOE
   Software Engineer
   
   Email: john.doe@example.com
   Phone: (555) 123-4567
   
   PROFESSIONAL SUMMARY
   Experienced software engineer with 5 years of Python development.
   
   SKILLS
   - Programming: Python, JavaScript, Java
   - Frameworks: Django, React, Flask
   - Cloud: AWS, Docker, Kubernetes
   - Databases: PostgreSQL, MongoDB
   - Other: Git, CI/CD, Agile
   
   EXPERIENCE
   Senior Developer | Tech Corp | 2020-Present
   - Built microservices with Python and AWS
   - Led team of 5 developers
   ---

5. ONLINE TOOLS TO CREATE PDF:
   - Google Docs (File > Download > PDF)
   - Microsoft Word (Save As > PDF)
   - https://www.pdf-online.com/osa/convert.aspx
   
6. SAMPLE RESUME REPOSITORIES:
   - https://github.com/resume/resume.github.com
   - Search for "sample resume PDF" online
    """)
    print("=" * 70)
    sys.exit(0)

# If file exists, test parsing
print(f"✓ Found resume file: {test_resume_path}")

print("\n[Step 3] Testing component-by-component...")
print("-" * 70)

try:
    # Test 1: Parse PDF to text
    print("\n1. PDF Parsing:")
    from resume_parser.parsers.pdf_parser import PDFParser
    parser = PDFParser()
    text = parser.parse(test_resume_path)
    print(f"   ✓ Extracted {len(text)} characters")
    print(f"   Preview: {text[:200]}...")
    
    # Test 2: Extract email
    print("\n2. Email Extraction:")
    email_extractor = EmailExtractor()
    email = email_extractor.extract(text)
    if email:
        print(f"   ✓ Found email: {email}")
    else:
        print(f"   ✗ No email found")
    
    # Test 3: Extract skills (if OpenAI API key is set)
    print("\n3. Skills Extraction (GPT-4):")
    try:
        skills_extractor = SkillsExtractor()
        print("   → Calling OpenAI API (this may take a few seconds)...")
        skills = skills_extractor.extract(text)
        if skills:
            print(f"   ✓ Found {len(skills)} skills:")
            for skill in skills[:10]:  # Show first 10
                print(f"      • {skill}")
            if len(skills) > 10:
                print(f"      ... and {len(skills) - 10} more")
        else:
            print(f"   ✗ No skills found")
    except Exception as e:
        print(f"   ✗ Skills extraction failed: {e}")
        print(f"   Make sure OPENAI_API_KEY is set in .env file")
    
    # Create final result
    print("\n" + "=" * 70)
    print("FINAL RESULT")
    print("=" * 70)
    
    result = ResumeData(
        name="[Name extraction needs SpaCy model]",
        email=email or "",
        skills=skills if 'skills' in locals() else []
    )
    
    import json
    print(json.dumps(result.to_dict(), indent=2))
    
except Exception as e:
    print(f"\n✗ Error during testing: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Testing complete!")
print("=" * 70)

