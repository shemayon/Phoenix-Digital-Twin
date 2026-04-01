"""Quick test to verify Gemini API key works."""

import google.generativeai as genai
from backend import constants

genai.configure(api_key=constants.GEMINI_API_KEY)
model = genai.GenerativeModel(constants.GEMINI_MODEL)

try:
    response = model.generate_content("Say 'Hello, API is working!' in one sentence.")
    print("✓ API Key is valid!")
    print(f"Response: {response.text}")
except Exception as e:
    print("✗ API call failed!")
    print(f"Error: {e}")
    print("\nThe API key may be invalid, expired, or you may need to:")
    print("1. Enable the Gemini API in Google Cloud Console")
    print("2. Check if there are billing/quota issues")
    print("3. Generate a new API key")
