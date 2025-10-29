# generate.py
import os
import google.generativeai as genai

# Get your Gemini API key (free for small use) from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY = os.getenv("AIzaSyDK9YwPo03lyypDUJG1md-KRoPLxlcQQkQ")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

def generate_answer(prompt: str, model: str = "gemini-1.5-flash", temperature: float = 0.0, max_output_tokens: int = 512):
    """
    Generate text using Google Gemini (free tier available).
    """
    model_instance = genai.GenerativeModel(model)
    response = model_instance.generate_content(
        prompt,
        generation_config={
            "temperature": temperature,
            "max_output_tokens": max_output_tokens
        }
    )
    return response.text.strip()
