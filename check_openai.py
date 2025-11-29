#!/usr/bin/env python3
"""
OpenAI API connectivity check script.

This script tests the connection to OpenAI's API and verifies that the API key
is properly configured. It performs a series of checks:

1. Verifies API key is set in environment variables
2. Validates API key format (should start with 'sk-')
3. Tests actual API connection with a minimal request
4. Checks model availability
5. Measures response time

The script provides clear, human-readable output indicating the status of each
check and troubleshooting suggestions if any checks fail.

Usage:
    python check_openai.py
    
    Or use the module function directly:
    from resume_parser.utils.openai_check import print_connectivity_status
    print_connectivity_status()

Exit Codes:
    0: Script completes (check results printed to stdout)
    
Note:
    Requires OPENAI_API_KEY environment variable or .env file configuration.
    See resume_parser.config for configuration details.
"""

from resume_parser.utils.openai_check import print_connectivity_status

if __name__ == "__main__":
    print_connectivity_status()

