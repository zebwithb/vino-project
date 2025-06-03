import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.GEMINI_KEY_API = os.getenv("GEMINI_KEY_API")
        if not self.GEMINI_KEY_API:
            raise ValueError("GEMINI_KEY_API environment variable is not set")
        self.PROJECT_NAME = "VINO API"
        self.VERSION = "1.0.0"

settings = Settings()