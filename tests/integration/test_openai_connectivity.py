"""Integration test for OpenAI API connectivity."""

import pytest
from resume_parser.utils.openai_check import check_openai_connectivity


@pytest.mark.integration
@pytest.mark.slow
class TestOpenAIConnectivity:
    """Test OpenAI API connectivity and configuration."""
    
    def test_openai_api_key_set(self):
        """Test that OpenAI API key is configured."""
        result = check_openai_connectivity()
        
        assert result['api_key_set'] is True, "OPENAI_API_KEY should be set in environment"
    
    def test_openai_api_key_format(self):
        """Test that API key has correct format."""
        from resume_parser.config import settings
        
        if not settings.openai_api_key:
            pytest.skip("OPENAI_API_KEY not set")
        
        # Skip if placeholder key
        placeholder_keys = ['your_api_key_here', 'sk-your-api-key-here', '']
        if settings.openai_api_key.lower() in [k.lower() for k in placeholder_keys]:
            pytest.skip("API key appears to be a placeholder")
        
        assert settings.openai_api_key.startswith('sk-'), \
            "API key should start with 'sk-'"
    
    def test_openai_connectivity(self):
        """Test actual connectivity to OpenAI API."""
        from resume_parser.config import settings
        
        # Skip if placeholder key
        placeholder_keys = ['your_api_key_here', 'sk-your-api-key-here', '']
        if not settings.openai_api_key or settings.openai_api_key.lower() in [k.lower() for k in placeholder_keys]:
            pytest.skip("OPENAI_API_KEY not set or is a placeholder - skipping connectivity test")
        
        result = check_openai_connectivity()
        
        if result['error'] and 'Authentication' in result['error']:
            pytest.skip(f"Authentication failed: {result['error']}")
        
        if result['error'] and 'format invalid' in result['error']:
            pytest.skip(f"API key format invalid: {result['error']}")
        
        # If we have an error, it's likely a connectivity issue
        if result['error']:
            pytest.fail(f"OpenAI connectivity check failed: {result['error']}")
        
        assert result['connected'] is True, "Should be able to connect to OpenAI API"
        assert result['api_key_valid'] is True, "API key should be valid"
        assert result['model_available'] is True, f"Model {result['model']} should be available"
        assert result['response_time_ms'] is not None, "Should have response time"
        assert result['response_time_ms'] > 0, "Response time should be positive"
        
        # Response time should be reasonable (less than 10 seconds)
        assert result['response_time_ms'] < 10000, \
            f"Response time ({result['response_time_ms']}ms) seems too slow"

