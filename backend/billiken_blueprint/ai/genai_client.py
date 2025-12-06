import os
from unittest.mock import MagicMock
from google import genai

if os.environ.get("GEMINI_API_KEY"):
    genai_client = genai.Client()
else:
    genai_client = MagicMock()