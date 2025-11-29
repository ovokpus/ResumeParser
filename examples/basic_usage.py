"""
Basic usage examples for Resume Parser Framework.

These examples demonstrate common use cases for the framework.
For testing, see the tests/ directory.
"""

import json
import logging
from pathlib import Path
from resume_parser import ResumeParserFramework

# Setup logging to see framework operations
logging.basicConfig(level=logging.INFO)


def example_1_parse_pdf():
    """Example 1: Parse a PDF resume."""
    print("\n" + "="*60)
    print("Example 1: Parse PDF Resume")
    print("="*60)
    
    framework = ResumeParserFramework()
    
    # Parse PDF resume (update path to your resume file)
    resume_path = "path/to/your/resume.pdf"  # Update this path
    if not Path(resume_path).exists():
        print(f"⚠ Resume file not found at: {resume_path}")
        print("   Update the path in this script to point to your resume file.")
        return
    
    resume_data = framework.parse_resume(resume_path)
    
    # Display results
    print("\nExtracted Data:")
    print(f"Name: {resume_data.name}")
    print(f"Email: {resume_data.email}")
    print(f"Skills ({len(resume_data.skills)}):")
    for skill in resume_data.skills:
        print(f"  - {skill}")
    
    # Convert to JSON
    print("\nJSON Output:")
    print(json.dumps(resume_data.to_dict(), indent=2))


def example_2_parse_word():
    """Example 2: Parse a Word document resume."""
    print("\n" + "="*60)
    print("Example 2: Parse Word Document Resume")
    print("="*60)
    
    framework = ResumeParserFramework()
    
    # Parse Word resume (update path to your resume file)
    resume_path = "path/to/your/resume.docx"  # Update this path
    if not Path(resume_path).exists():
        print(f"⚠ Resume file not found at: {resume_path}")
        print("   Update the path in this script to point to your resume file.")
        return
    
    resume_data = framework.parse_resume(resume_path)
    
    print("\nExtracted Data:")
    print(json.dumps(resume_data.to_dict(), indent=2))


def example_3_batch_processing():
    """Example 3: Batch process multiple resumes."""
    print("\n" + "="*60)
    print("Example 3: Batch Process Multiple Resumes")
    print("="*60)
    
    framework = ResumeParserFramework()
    
    # List of resume files (update paths to your resume files)
    resume_files = [
        "path/to/resume1.pdf",
        "path/to/resume2.docx",
        "path/to/resume3.pdf",
    ]
    
    results = []
    for file_path in resume_files:
        try:
            resume_data = framework.parse_resume(file_path)
            results.append({
                "file": file_path,
                "data": resume_data.to_dict(),
                "status": "success"
            })
            print(f"[OK] Processed: {file_path}")
        except Exception as e:
            results.append({
                "file": file_path,
                "error": str(e),
                "status": "failed"
            })
            print(f"[FAIL] Failed: {file_path} - {str(e)}")
    
    # Save results
    output_file = "batch_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")


def example_4_error_handling():
    """Example 4: Demonstrate error handling."""
    print("\n" + "="*60)
    print("Example 4: Error Handling")
    print("="*60)
    
    framework = ResumeParserFramework()
    
    # Test various error scenarios
    test_cases = [
        ("nonexistent.pdf", "File not found"),
        ("path/to/corrupted.pdf", "Parsing error"),
        ("path/to/empty.docx", "Empty content"),
    ]
    
    for file_path, expected_error in test_cases:
        try:
            resume_data = framework.parse_resume(file_path)
            print(f"[OK] Unexpected success: {file_path}")
        except FileNotFoundError:
            print(f"[OK] Caught FileNotFoundError: {file_path}")
        except Exception as e:
            print(f"[OK] Caught {type(e).__name__}: {file_path} - {str(e)}")


if __name__ == "__main__":
    # Run all examples
    example_1_parse_pdf()
    example_2_parse_word()
    example_3_batch_processing()
    example_4_error_handling()
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)

