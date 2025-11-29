"""Utility to test OpenAI API connectivity."""

from typing import Dict, Optional
from openai import OpenAI
from openai import AuthenticationError, APIError, APIConnectionError

from resume_parser.config import settings
from resume_parser.utils.logger import setup_logger

logger = setup_logger(__name__)


def check_openai_connectivity() -> Dict[str, any]:
    """
    Test connectivity to OpenAI API.
    
    Returns:
        Dictionary with connectivity status and details:
        {
            'connected': bool,
            'api_key_set': bool,
            'api_key_valid': bool,
            'model_available': bool,
            'error': Optional[str],
            'model': Optional[str],
            'response_time_ms': Optional[float]
        }
    """
    result = {
        'connected': False,
        'api_key_set': False,
        'api_key_valid': False,
        'model_available': False,
        'error': None,
        'model': settings.openai_model,
        'response_time_ms': None
    }
    
    # Check if API key is set
    if not settings.openai_api_key:
        result['error'] = 'OPENAI_API_KEY not set in environment'
        return result
    
    result['api_key_set'] = True
    
    # Check API key format
    if not settings.openai_api_key.startswith('sk-'):
        result['error'] = 'API key format invalid (should start with "sk-")'
        return result
    
    # Try to make a simple API call
    try:
        import time
        client = OpenAI(api_key=settings.openai_api_key)
        
        # Make a minimal test call
        start_time = time.time()
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'OK' if you can read this."}
            ],
            max_tokens=10,
            temperature=0
        )
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Check if we got a response
        if response and response.choices:
            result['connected'] = True
            result['api_key_valid'] = True
            result['model_available'] = True
            result['response_time_ms'] = round(response_time, 2)
            logger.info(f"OpenAI connectivity check passed. Response time: {result['response_time_ms']}ms")
        else:
            result['error'] = 'Received empty response from OpenAI'
            
    except AuthenticationError as e:
        result['error'] = f'Authentication failed: {str(e)}'
        logger.error(f"OpenAI authentication error: {e}")
        
    except APIConnectionError as e:
        result['error'] = f'Connection failed: {str(e)}'
        logger.error(f"OpenAI connection error: {e}")
        
    except APIError as e:
        result['error'] = f'API error: {str(e)}'
        logger.error(f"OpenAI API error: {e}")
        
    except Exception as e:
        result['error'] = f'Unexpected error: {str(e)}'
        logger.error(f"Unexpected error checking OpenAI connectivity: {e}")
    
    return result


def print_connectivity_status() -> None:
    """Print a human-readable connectivity status."""
    result = check_openai_connectivity()
    
    print("=" * 60)
    print("OpenAI API Connectivity Check")
    print("=" * 60)
    
    print(f"\nAPI Key Set: {'[OK]' if result['api_key_set'] else '[FAIL]'}")
    print(f"API Key Valid: {'[OK]' if result['api_key_valid'] else '[FAIL]'}")
    print(f"Connected: {'[OK]' if result['connected'] else '[FAIL]'}")
    print(f"Model Available: {'[OK]' if result['model_available'] else '[FAIL]'}")
    print(f"Model: {result['model']}")
    
    if result['response_time_ms']:
        print(f"Response Time: {result['response_time_ms']}ms")
    
    if result['error']:
        print(f"\nError: {result['error']}")
    
    print("=" * 60)
    
    if result['connected']:
        print("[OK] OpenAI API is accessible and working correctly!")
    else:
        print("[FAIL] OpenAI API connectivity check failed.")
        print("\nTroubleshooting:")
        if not result['api_key_set']:
            print("  - Set OPENAI_API_KEY in your .env file")
        elif not result['api_key_valid']:
            print("  - Verify your API key is correct and starts with 'sk-'")
        elif result['error']:
            print(f"  - {result['error']}")
    
    print()

