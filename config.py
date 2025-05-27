import os
from dotenv import load_dotenv

# Load .env file if present (only affects local dev, safe to call always)
load_dotenv()

class Config:
    # Comma-separated API keys (string → list)
    API_KEYS = os.getenv("API_KEYS", "").split(",")
    FIRESTORE_CREDENTIALS = os.getenv("FIRESTORE_CREDENTIALS", "")  # Placeholder for later
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    PORT = int(os.getenv("PORT", 8080))
