"""Data models for resume parsing."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ResumeData:
    """
    Represents parsed resume data.
    
    Attributes:
        name: Full name of the candidate (e.g., "John Doe")
        email: Email address of the candidate (e.g., "john.doe@example.com")
        skills: List of technical and professional skills (e.g., ["Python", "AWS", "Leadership"])
    """
    name: str
    email: str
    skills: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        # Normalize name
        if self.name:
            self.name = " ".join(self.name.split())  # Remove extra whitespace
        
        # Normalize email
        if self.email:
            self.email = self.email.lower().strip()
        
        # Deduplicate and normalize skills
        if self.skills:
            # Remove duplicates while preserving order, normalize casing
            seen = set()
            normalized_skills = []
            for skill in self.skills:
                skill_normalized = skill.strip()
                skill_lower = skill_normalized.lower()
                if skill_lower not in seen and skill_normalized:
                    seen.add(skill_lower)
                    normalized_skills.append(skill_normalized)
            self.skills = normalized_skills
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "email": self.email,
            "skills": self.skills
        }

