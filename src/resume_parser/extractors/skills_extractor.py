"""Skills extractor using GPT-4."""

import json
from typing import List
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from resume_parser.extractors.base import FieldExtractor
from resume_parser.exceptions import ExtractionError, APIError
from resume_parser.config import settings
from resume_parser.utils.logger import setup_logger

logger = setup_logger(__name__)


class SkillsExtractor(FieldExtractor):
    """
    Extract skills from resume text using GPT-4.
    
    Uses OpenAI's GPT-4 Turbo with carefully engineered prompts to:
    - Identify technical and professional skills
    - Handle various skill formats (bullet points, paragraphs, tables)
    - Provide structured JSON output
    - Deduplicate and normalize skill names
    """
    
    # System prompt for GPT-4
    SYSTEM_PROMPT = """You are an expert resume parser specializing in extracting skills from resumes.

Your task is to identify and extract ALL technical and professional skills mentioned in the resume text.

Skills can include:
- Programming languages (Python, JavaScript, Java, etc.)
- Frameworks and libraries (React, Django, TensorFlow, etc.)
- Tools and platforms (Docker, Kubernetes, AWS, Git, etc.)
- Databases (PostgreSQL, MongoDB, Redis, etc.)
- Methodologies (Agile, Scrum, TDD, CI/CD, etc.)
- Soft skills (Leadership, Communication, Problem-solving, etc.)
- Domain expertise (Machine Learning, Data Analysis, Cloud Architecture, etc.)

Guidelines:
1. Extract skills exactly as they appear (preserve casing: "Python" not "python")
2. Remove duplicates (e.g., "Python" and "python programming" → just "Python")
3. Return specific technologies, not categories (e.g., "React" not "frontend frameworks")
4. Include both hard skills and relevant soft skills
5. If a skill appears multiple times in different contexts, include it only once
6. Do not invent skills that aren't mentioned in the resume

Return ONLY a valid JSON object with a "skills" array. No additional text or explanation.

Example output:
{"skills": ["Python", "Machine Learning", "AWS", "Docker", "Team Leadership"]}"""
    
    def __init__(self):
        """Initialize OpenAI client and validate configuration."""
        try:
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
            self.max_tokens = settings.openai_max_tokens
            self.temperature = settings.openai_temperature
            logger.info(f"Initialized SkillsExtractor with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise ExtractionError(f"OpenAI initialization failed: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(APIError),
        reraise=True
    )
    def extract(self, text: str) -> List[str]:
        """
        Extract skills from resume text using GPT-4.
        
        Args:
            text: Resume text content
        
        Returns:
            List of extracted skills
        
        Raises:
            ExtractionError: If extraction fails
            APIError: If OpenAI API call fails (with retry)
        """
        self._validate_text_input(text)
        
        logger.info("Extracting skills using GPT-4")
        
        try:
            # Truncate text if too long (GPT-4 context limit consideration)
            max_chars = 15000  # ~3750 tokens
            if len(text) > max_chars:
                logger.warning(
                    f"Resume text ({len(text)} chars) exceeds limit, truncating to {max_chars}"
                )
                text = text[:max_chars]
            
            # Create user prompt
            user_prompt = f"""Extract all skills from the following resume text:

{text}

Return ONLY the JSON object with the skills array."""
            
            # Call OpenAI API
            logger.debug(f"Calling OpenAI API with model: {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}  # Enforce JSON output
            )
            
            # Extract and parse response
            content = response.choices[0].message.content
            logger.debug(f"GPT-4 response: {content}")
            
            # Parse JSON response
            result = json.loads(content)
            skills = result.get("skills", [])
            
            # Validate and limit skills
            if not isinstance(skills, list):
                raise ExtractionError("GPT-4 returned invalid skills format")
            
            # Filter out empty strings and limit to max skills
            skills = [s.strip() for s in skills if s and s.strip()]
            skills = skills[:settings.max_skills_returned]
            
            logger.info(f"Successfully extracted {len(skills)} skills using GPT-4")
            logger.debug(f"Extracted skills: {skills}")
            
            # Log token usage for cost tracking
            usage = response.usage
            logger.info(
                f"Token usage - Prompt: {usage.prompt_tokens}, "
                f"Completion: {usage.completion_tokens}, "
                f"Total: {usage.total_tokens}"
            )
            
            return skills
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT-4 JSON response: {str(e)}")
            raise ExtractionError(f"Invalid JSON response from GPT-4: {str(e)}")
        
        except Exception as e:
            # Distinguish between retryable API errors and fatal errors
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ['rate limit', 'timeout', 'connection']):
                logger.warning(f"Retryable API error: {str(e)}")
                raise APIError(f"OpenAI API error: {str(e)}")
            else:
                logger.error(f"Fatal error extracting skills: {str(e)}")
                raise ExtractionError(f"Failed to extract skills: {str(e)}")

