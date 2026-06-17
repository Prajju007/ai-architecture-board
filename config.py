import os

from dotenv import load_dotenv

load_dotenv()


GPT_MODEL = "gpt-4o"

GEMINI_MODEL = "gemini-3.1-pro-preview"


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")