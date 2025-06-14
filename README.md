# Firestore Adapter

This service exposes a minimal REST API for interacting with Google Firestore. It is intended for deployment on Cloud Run.

## Setup

1. Copy `.env.example` to `.env` and fill in the required values. If you deploy
   without an `.env` file, the service automatically reads API keys from the
   Secret Manager secret **fs-adapter-api-key**.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application locally:
   ```bash
   python app.py
   ```

## Running Tests

```bash
pytest -q
```

## Deployment

The GitHub workflow builds a Docker image and deploys to Cloud Run. The service expects authenticated access via API keys. You can provide the keys directly using the `API_KEYS` environment variable or rely on the built-in Secret Manager integration, which reads keys from the **fs-adapter-api-key** secret at startup. Ensure Cloud Run authentication matches your needs.


