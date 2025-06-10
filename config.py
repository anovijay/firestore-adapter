import os
import sys
import json
import logging
from dotenv import load_dotenv

# Load .env file if present (only affects local dev, safe to call always)
load_dotenv()

class Config:
    # Comma-separated API keys (string → list)
    API_KEYS = os.getenv("API_KEYS", "").split(",")
    FIRESTORE_CREDENTIALS = os.getenv("FIRESTORE_CREDENTIALS", "")  # Placeholder for later
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    PORT = int(os.getenv("PORT", 8080))


def validate_config():
    if not any(k.strip() for k in Config.API_KEYS):
        logging.error("API_KEYS environment variable must not be empty")
        sys.exit(1)

    creds = Config.FIRESTORE_CREDENTIALS
    if not creds:
        logging.error("FIRESTORE_CREDENTIALS must be set to a path or JSON string")
        sys.exit(1)

    if os.path.isfile(creds):
        return
    try:
        json.loads(creds)
    except json.JSONDecodeError:
        logging.error("FIRESTORE_CREDENTIALS must point to an existing file or valid JSON")
        sys.exit(1)
