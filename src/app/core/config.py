import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        if not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        self.PROJECT_NAME = "VINO API"
        self.VERSION = "1.0.0"

settings = Settings()