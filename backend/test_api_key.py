import sys
import os
from google import genai

# Adjust path to import backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.gemini_service import get_gemini_client

def test():
    print("Testing Gemini API Connection...")
    try:
        client = get_gemini_client()
        print("Client initialized successfully.")
        
        print("Calling Gemini model...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Say 'Connection Successful!'"
        )
        print(f"Response: {response.text}")
        print("SUCCESS: Gemini API is fully operational with this key!")
    except Exception as e:
        print(f"FAILED: Could not connect to Gemini. Error: {e}")

if __name__ == "__main__":
    test()
