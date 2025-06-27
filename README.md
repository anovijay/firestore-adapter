# Firestore Adapter

A RESTful API service for managing Firestore documents with advanced querying capabilities.

## Features

- **CRUD Operations**: Create, read, update, and delete documents
- **Advanced Querying**: Filter, sort, paginate, and select specific fields
- **Authentication**: API key-based security
- **Flexible Schema**: Support for any document structure
- **Cloud Run Ready**: Optimized for serverless deployment

## API Documentation

### OpenAPI Specification
The complete API documentation is available as an OpenAPI 3.0 specification:
- **Specification file**: `/openapi.yaml`
- **Interactive documentation**: Use any OpenAPI-compatible tool (Swagger UI, Postman, etc.)

## Configuration
This service uses a hardcoded API key for authentication. For security, you should change the default key before deploying to a production environment.

-   **Location**: Edit the `API_KEYS` list in the `config.py` file.
-   **Security**: Ensure this file is properly secured and not publicly exposed.

### Quick Start

1. **Authentication**: Include your API key from `config.py` in the `X-API-KEY` header
2. **Base URL**: `https://your-service-url.com` (or `http://localhost:8080` for local development)

### Example Requests

```bash
# Create a document
curl -X POST https://your-service-url.com/documents/users \
  -H "X-API-KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'

# Query documents with filters
curl "https://your-service-url.com/documents/users?age_gte=18&status=active" \
  -H "X-API-KEY: your-api-key"

# Update a document
curl -X PUT https://your-service-url.com/documents/users/user123 \
  -H "X-API-KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"status": "inactive"}'
```

## Advanced Querying

- **Filters**: `field_gte`, `field_lte`, `field_gt`, `field_lt`, `field_in`, `field=value`
- **Sorting**: `order_by=field` or `order_by=-field` (descending)
- **Pagination**: `limit` and `offset` parameters
- **Field Selection**: `fields=field1,field2`

## Development

### Local Setup
```bash
pip install -r requirements.txt
export API_KEYS="your-test-key"
python app.py
```

### Deployment
Use the included deployment scripts or GitHub Actions workflow for Cloud Run deployment.

## Architecture

This service follows a simplified two-file structure:
- **`app.py`**: The main Flask application that defines all API endpoints.
- **`core.py`**: A consolidated module containing authentication and helper logic.
- **`config.py`**: Manages configuration, including the hardcoded API keys.

- **Environment Variables**: The `API_KEYS` environment variable can also be used to add temporary keys for local testing.
- **Service Account**: Uses the attached Cloud Run service account for Firestore authentication.


