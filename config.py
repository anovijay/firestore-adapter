import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

class Config:
    """
    Simplified configuration with a hardcoded API key.
    IMPORTANT: Change the value of API_KEYS for your production environment.
    """
    # --- HARDCODED API KEYS ---
    # Add one or more keys to this list.
    API_KEYS = [
        "sk_rhea_fsadapterapikey_1229539",
        "sk_rhea_fsadapterapikey_testonly"
    ]
    
    # This environment variable can still be used to add keys for local testing,
    # but the list above will be the primary source.
    ENV_API_KEYS = [k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()]

    # Combine them
    ALL_API_KEYS = list(set(API_KEYS + ENV_API_KEYS))

    FIRESTORE_CREDENTIALS = os.getenv("FIRESTORE_CREDENTIALS", "")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    PORT = int(os.getenv("PORT", 8080))

def validate_config():
    """Basic validation to ensure at least one key is set."""
    if not Config.ALL_API_KEYS:
        raise ValueError("Configuration Error: At least one API key must be defined in config.py")
