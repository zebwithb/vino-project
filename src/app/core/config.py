import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.PROJECT_NAME = "AI Text Utility API"
        self.VERSION = "1.1.0"

settings = Settings()