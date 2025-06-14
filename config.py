import os
import sys
import json
import logging
from dotenv import load_dotenv
from google.cloud import secretmanager

# Load .env file if present (only affects local dev, safe to call always)
load_dotenv()


def load_api_keys_from_secret_manager():
    """Populate API_KEYS from Secret Manager if not set."""
    if os.getenv("API_KEYS"):
        return

    secret_name = os.getenv("API_KEYS_SECRET_NAME")
    if not secret_name:
        # Nothing to load
        return

    project_id = os.getenv("GCP_PROJECT") or os.getenv("PROJECT_ID")
    if secret_name.startswith("projects/"):
        secret_path = f"{secret_name}/versions/latest"
    elif project_id:
        secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    else:
        logging.error("API_KEYS_SECRET_NAME set but project ID missing")
        return

    try:
        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(name=secret_path)
        secret_value = response.payload.data.decode("utf-8")
        os.environ["API_KEYS"] = secret_value
        logging.info("Loaded API keys from Secret Manager")
    except Exception:
        logging.exception("Failed to load API keys from Secret Manager")


load_api_keys_from_secret_manager()

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
