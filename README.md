# Firestore Adapter

This service exposes a minimal REST API for interacting with Google Firestore. It is intended for deployment on Cloud Run.

## Setup

1. Copy `.env.example` to `.env` and fill in the required values.
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

The GitHub workflow builds a Docker image and deploys to Cloud Run. The service expects authenticated access via API keys. Update `API_KEYS` in your environment configuration and ensure Cloud Run authentication matches your needs.

