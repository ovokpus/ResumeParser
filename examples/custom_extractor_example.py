"""
Example of extending the framework with custom extractors.

This demonstrates how to create custom field extractors and integrate
them with the framework.
"""

import re
from pathlib import Path
from typing import List
from resume_parser.extractors.base import FieldExtractor
from resume_parser.core.resume_extractor import ResumeExtractor
from resume_parser import ResumeParserFramework


class CustomPhoneExtractor(FieldExtractor):
    """
    Custom extractor for phone numbers.
    
    This demonstrates how to create a new field extractor
    following the framework's architecture.
    """
    
    PHONE_PATTERN = re.compile(
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    )
    
    def extract(self, text: str) -> str:
        """Extract phone number from text."""
        self._validate_text_input(text)
        
        matches = self.PHONE_PATTERN.findall(text)
        if matches:
            return matches[0]
        return ""


class EnhancedNameExtractor(FieldExtractor):
    """
    Enhanced name extractor with additional validation.
    
    Demonstrates customizing existing extraction logic.
    """
    
    def extract(self, text: str) -> str:
        """Extract name with enhanced validation."""
        self._validate_text_input(text)
        
        # Your custom name extraction logic
        lines = text.split('\n')
        for line in lines[:3]:
            line = line.strip()
            if self._looks_like_name(line):
                return line
        return ""
    
    def _looks_like_name(self, text: str) -> bool:
        """Enhanced name validation."""
        # Custom validation logic
        if not text or len(text) < 5:
            return False
        
        words = text.split()
        if len(words) < 2 or len(words) > 4:
            return False
        
        # Add your custom rules here
        return True


def main():
    """Demonstrate custom extractor usage."""
    print("Custom Extractor Example")
    print("="*60)
    
    # Option 1: Use custom extractor with existing framework
    custom_extractor = ResumeExtractor(
        name_extractor=EnhancedNameExtractor()
    )
    framework = ResumeParserFramework(resume_extractor=custom_extractor)
    
    resume_path = "path/to/your/resume.pdf"  # Update this path
    if not Path(resume_path).exists():
        print(f"⚠ Resume file not found at: {resume_path}")
        print("   Update the path in this script to point to your resume file.")
        return
    
    result = framework.parse_resume(resume_path)
    print(f"Name (with custom extractor): {result.name}")
    
    # Option 2: Standalone usage
    phone_extractor = CustomPhoneExtractor()
    text = "Contact me at (555) 123-4567 for more info."
    phone = phone_extractor.extract(text)
    print(f"Extracted phone: {phone}")


if __name__ == "__main__":
    main()

