"""Test which Gemini models are available"""
import google.generativeai as genai
from config.settings import settings

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

print("🔍 Fetching available models...\n")

try:
    models = genai.list_models()
    
    print("📋 Available models that support generateContent:\n")
    
    for model in models:
        # Check if model supports generateContent
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
            print(f"   Display name: {model.display_name}")
            print(f"   Description: {model.description[:80]}...")
            print()
            
except Exception as e:
    print(f"❌ Error: {e}")