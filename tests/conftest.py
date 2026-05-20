"""
Pytest configuration — sets up the test environment before any module is imported.

OPENAI_API_KEY is set to a placeholder so the OpenAI client can be instantiated
at module level (in guardrails.py) without raising an authentication error.
All tests that touch the client mock it, so this value is never sent to OpenAI.
"""
import os

os.environ.setdefault("OPENAI_API_KEY", "test-key-not-used-by-mocked-tests")
