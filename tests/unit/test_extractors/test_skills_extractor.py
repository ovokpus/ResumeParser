"""Unit tests for SkillsExtractor."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from resume_parser.extractors.skills_extractor import SkillsExtractor
from resume_parser.exceptions import ExtractionError, APIError


class TestSkillsExtractor:
    """Test suite for SkillsExtractor."""
    
    @patch('resume_parser.extractors.skills_extractor.OpenAI')
    def setup_method(self, mock_openai):
        """Setup test fixture with mocked OpenAI."""
        self.mock_client = MagicMock()
        mock_openai.return_value = self.mock_client
        self.extractor = SkillsExtractor()
    
    def test_extract_skills_success(self, sample_resume_text):
        """Test successful skills extraction."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''
        {
            "skills": ["Python", "JavaScript", "AWS", "Docker", "Kubernetes"]
        }
        '''
        mock_response.usage.prompt_tokens = 500
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 550
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Execute
        result = self.extractor.extract(sample_resume_text)
        
        # Verify
        assert isinstance(result, list)
        assert len(result) == 5
        assert "Python" in result
        assert "AWS" in result
        
        # Verify API was called correctly
        self.mock_client.chat.completions.create.assert_called_once()
        call_kwargs = self.mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['model'] == self.extractor.model
        assert call_kwargs['temperature'] == self.extractor.temperature
        assert 'messages' in call_kwargs
    
    def test_extract_skills_empty_result(self):
        """Test when GPT-4 returns no skills."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"skills": []}'
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 10
        mock_response.usage.total_tokens = 110
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        result = self.extractor.extract("Some text")
        assert result == []
    
    def test_extract_skills_filters_empty_strings(self):
        """Test that empty strings are filtered from results."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''
        {"skills": ["Python", "", "AWS", "  ", "Docker"]}
        '''
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 120
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        result = self.extractor.extract("Some text")
        assert len(result) == 3
        assert "" not in result
    
    def test_extract_skills_limits_max_skills(self):
        """Test that results are limited to max_skills_returned."""
        skills = [f"Skill{i}" for i in range(50)]  # 50 skills
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = f'{{"skills": {skills}}}'
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 100
        mock_response.usage.total_tokens = 200
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        result = self.extractor.extract("Some text")
        assert len(result) <= 20  # Based on default max_skills_returned
    
    def test_extract_skills_invalid_json(self):
        """Test handling of invalid JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'Invalid JSON {{'
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        with pytest.raises(ExtractionError, match="Invalid JSON"):
            self.extractor.extract("Some text")
    
    def test_extract_skills_truncates_long_text(self):
        """Test that very long text is truncated."""
        long_text = "A" * 20000  # 20k characters
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"skills": ["Python"]}'
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 10
        mock_response.usage.total_tokens = 110
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        result = self.extractor.extract(long_text)
        
        # Verify truncation occurred by checking API call
        call_kwargs = self.mock_client.chat.completions.create.call_args[1]
        user_message = call_kwargs['messages'][1]['content']
        assert len(user_message) < 20000
    
    def test_empty_text_raises_error(self):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="empty text"):
            self.extractor.extract("")

