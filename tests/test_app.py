import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from core import FirestoreClient # Import the class to mock it
from google.api_core.exceptions import NotFound

# The API key to be used in tests, matching what the test client is configured with
TEST_API_KEY = "test-key"

@pytest.fixture
def mock_firestore_client():
    """Provides a mock of the FirestoreClient for dependency injection."""
    with patch('core.FirestoreClient', autospec=True) as MockFirestore:
        # Create an instance of the mock
        mock_instance = MockFirestore.return_value
        yield mock_instance

@pytest.fixture
def client(mock_firestore_client):
    """Create and configure a new app instance for each test, with a mocked Firestore client."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "API_KEYS": [TEST_API_KEY],
        "FIRESTORE_CREDENTIALS": "" # Ensure it doesn't try to load real credentials
    })
    
    # Replace the real client with our mock before the test runs
    app.extensions["firestore_client"] = mock_firestore_client
    
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "success"

def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Firestore Adapter service is running" in response.json["message"]

def test_unauthorized_access(client):
    """Test that requests without an API key are rejected."""
    response = client.get("/documents/users")
    assert response.status_code == 401
    assert response.json["message"] == "Unauthorized"

def test_wrong_api_key(client):
    """Test that requests with an incorrect API key are rejected."""
    headers = {"X-API-KEY": "wrong-key"}
    response = client.get("/documents/users", headers=headers)
    assert response.status_code == 401
    assert response.json["message"] == "Unauthorized"

def test_get_document_authorized(client, mock_firestore_client):
    """Test getting a document with a valid API key."""
    mock_firestore_client.read_document.return_value = {"id": "test-doc", "data": "some data"}
    headers = {"X-API-KEY": TEST_API_KEY}
    response = client.get("/documents/users/test-doc", headers=headers)
    assert response.status_code == 200
    assert response.json["data"]["id"] == "test-doc"
    mock_firestore_client.read_document.assert_called_once_with("users", "test-doc")

def test_get_document_not_found(client, mock_firestore_client):
    """Test getting a document that does not exist."""
    mock_firestore_client.read_document.return_value = None
    headers = {"X-API-KEY": TEST_API_KEY}
    response = client.get("/documents/users/non-existent-doc", headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json["message"]

def test_create_document(client, mock_firestore_client):
    """Test creating a document."""
    mock_firestore_client.create_document.return_value = {"id": "new-doc", "name": "test"}
    headers = {"X-API-KEY": TEST_API_KEY}
    data = {"name": "test"}
    response = client.post("/documents/users", headers=headers, json=data)
    assert response.status_code == 201
    assert response.json["data"]["id"] == "new-doc"
    mock_firestore_client.create_document.assert_called_once_with("users", data)

def test_update_document(client, mock_firestore_client):
    """Test updating a document."""
    mock_firestore_client.update_document.return_value = {"id": "test-doc", "name": "updated"}
    headers = {"X-API-KEY": TEST_API_KEY}
    data = {"name": "updated"}
    response = client.put("/documents/users/test-doc", headers=headers, json=data)
    assert response.status_code == 200
    assert response.json["data"]["name"] == "updated"
    mock_firestore_client.update_document.assert_called_once_with("users", "test-doc", data)

def test_update_document_not_found(client, mock_firestore_client):
    """Test updating a non-existent document."""
    mock_firestore_client.update_document.side_effect = NotFound("Test not found")
    headers = {"X-API-KEY": TEST_API_KEY}
    data = {"name": "updated"}
    response = client.put("/documents/users/non-existent-doc", headers=headers, json=data)
    assert response.status_code == 404
    assert "not found" in response.json["message"]

def test_delete_document(client, mock_firestore_client):
    """Test deleting a document."""
    mock_firestore_client.delete_document.return_value = {"id": "test-doc"}
    headers = {"X-API-KEY": TEST_API_KEY}
    response = client.delete("/documents/users/test-doc", headers=headers)
    assert response.status_code == 200
    assert response.json["data"]["id"] == "test-doc"
    mock_firestore_client.delete_document.assert_called_once_with("users", "test-doc") 