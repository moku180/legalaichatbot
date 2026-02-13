import os
import sys
from pathlib import Path
from google import genai
from dotenv import load_dotenv

# Add backend to sys.path
backend_path = Path("c:/Users/moksh/OneDrive/Desktop/legalchatbot/backend")
sys.path.append(str(backend_path))

# Load .env
load_dotenv(backend_path / ".env")

api_key = os.getenv("GEMINI_API_KEY")
print(f"Using API Key: {api_key[:5]}...")

client = genai.Client(api_key=api_key)

try:
    print("Listing models...")
    # The new SDK might return an iterator of Model objects
    for model in client.models.list():
        print(f"Name: {model.name}")
        if hasattr(model, 'display_name'):
            print(f"  DisplayName: {model.display_name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"  Supported wrapper: {model.supported_generation_methods}")
        print("-" * 20)
except Exception as e:
    print(f"Error listing models: {e}")
    import traceback
    traceback.print_exc()
