# Firestore Adapter

A RESTful API service for managing Firestore documents with advanced querying capabilities, optimized for serverless deployment on Google Cloud Run.

## Features

- **CRUD Operations**: Create, read, update, and delete documents.
- **Advanced Querying**: Filter, sort, paginate, and select specific fields.
- **Secure Authentication**: API key security managed via Google Secret Manager.
- **Flexible Schema**: Supports any document structure.
- **Cloud Run Ready**: Containerized and configured for easy deployment.

## API Documentation

The complete API documentation is available as an OpenAPI 3.0 specification. The service serves the spec at the `/openapi.yaml` endpoint.

- **Specification file**: `openapi.yaml`
- **Interactive documentation**: Use any OpenAPI-compatible tool (like Swagger UI or Postman) with the spec.

## Configuration

API keys for authentication are managed centrally in **Google Cloud Secret Manager**.

- **Secret Name**: `fs-adapter-api-key`
- **Format**: The secret should contain a comma-separated list of valid API keys.
- **Permissions**: The Cloud Run service account requires the **Secret Manager Secret Accessor** IAM role to read the keys.

The service loads these keys at startup. There is no need to edit local configuration files for keys.

## Development

### Local Setup
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Authenticate with Google Cloud**:
    Required for accessing secrets and Firestore.
    ```bash
    gcloud auth application-default login
    ```
3.  **Run the Service**:
    ```bash
    python app.py
    ```
    The service will run on `http://localhost:8080`.

### End-to-End Testing
The project includes a script to run live tests against a deployed instance of the service. It performs a full CRUD lifecycle to ensure all endpoints are working correctly.

1.  **Set Project ID**:
    Export the `GCP_PROJECT_ID` environment variable.
    ```bash
    export GCP_PROJECT_ID="your-gcp-project-id"
    ```
2.  **Run Tests**:
    ```bash
    python e2etests.py
    ```

## Architecture

This service follows a simplified and robust structure:
- **`app.py`**: The main Flask application factory. It initializes the app, sets up the Firestore client, and defines all API endpoints.
- **`core.py`**: A consolidated module containing core logic for authentication (API key checks), Firestore interactions, error handling, and logging.
- **`config.py`**: Manages environment-based configuration but **does not** handle secrets.
- **`e2etests.py`**: Script for running live end-to-end tests against a deployed service instance.


