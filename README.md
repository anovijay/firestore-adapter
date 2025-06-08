# Firestore Adapter

This service provides a simple HTTP API for interacting with Google Firestore. It is designed to be deployed to Cloud Run but can also be run locally using Flask's development server.

## Environment Variables

Configuration is loaded from environment variables (usually via a `.env` file when running locally). Duplicate keys have been removed and the main variables are documented below:

| Variable | Description |
|----------|-------------|
| `API_KEYS` | Comma-separated list of valid API keys allowed to access the API. |
| `FIRESTORE_CREDENTIALS` | Path to the service account JSON file used by the Firestore client. |
| `GOOGLE_APPLICATION_CREDENTIALS` | Alternative credentials file if you do not set `FIRESTORE_CREDENTIALS`. |
| `FIRESTORE_PROJECT_ID` | GCP project containing the Firestore database. |
| `PROJECT_ID` | Project ID used during deployment scripts. |
| `SERVICE_NAME` | Name of the Cloud Run service. |
| `REGION` | Deployment region for Cloud Run. |
| `SERVICE_ACCOUNT_EMAIL` | Service account used when deploying. |
| `USE_LOCAL_USER` | Set to `true` to use local gcloud credentials. |
| `KEY_FILE` | Key file used when `USE_LOCAL_USER` is `false`. |
| `DEBUG` | Enable Flask debug mode when set to `True`. |
| `PORT` | Port for the Flask server. Default is `8080`. |

Create a `.env` file based on `.env.example` and fill in the appropriate values before running the application locally.

## Running Locally

Install the dependencies and run the Flask app:

```bash
pip install -r requirements.txt
python app.py
```

The service will start on `http://localhost:8080` by default.

