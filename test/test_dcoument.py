import pytest
from unittest.mock import patch, MagicMock
from src.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_list_documents(client):
    with patch("src.routes.documents.client") as mock_client:
        mock_client.list_documents.return_value = [{"id": "1"}]
        response = client.get("/documents/")
        assert response.status_code == 200
        assert response.json == [{"id": "1"}]

def test_get_document_found(client):
    with patch("src.routes.documents.client") as mock_client:
        mock_client.get_document.return_value = {"id": "1", "field": "value"}
        response = client.get("/documents/1")
        assert response.status_code == 200
        assert response.json == {"id": "1", "field": "value"}

def test_get_document_not_found(client):
    with patch("src.routes.documents.client") as mock_client:
        mock_client.get_document.return_value = None
        response = client.get("/documents/notfound")
        assert response.status_code == 404

def test_add_document(client):
    with patch("src.routes.documents.client") as mock_client:
        mock_client.add_document.return_value = "2"
        data = {"field": "value"}
        response = client.post("/documents/", json=data)
        assert response.status_code == 201
        assert "id" in response.json

def test_update_document(client):
    with patch("src.routes.documents.client") as mock_client:
        mock_client.update_document.return_value = True
        data = {"field": "new_value"}
        response = client.put("/documents/1", json=data)
        assert response.status_code == 200
        assert response.json["message"] == "Document updated successfully"

def test_delete_document(client):
    with patch("src.routes.documents.client") as mock_client:
        mock_client.delete_document.return_value = True
        response = client.delete("/documents/1")
        assert response.status_code == 200
        assert response.json["message"] == "Document deleted successfully"
def test_get_document_success(client):
    with patch("src.routes.documents.client") as mock_client:
        mock_client.get_document.return_value = {"id": "1", "field1": "value1"}
        response = client.get("/documents/1")
        assert response.status_code == 200
        assert response.json == {"id": "1", "field1": "value1"}

def test_get_document_not_found(client):
    with patch("src.routes.documents.client") as mock_client:
        mock_client.get_document.return_value = None
        response = client.get("/documents/1")
        assert response.status_code == 404
        assert response.json["status"] == "error"
        assert "not found" in response.json["message"].lower()

def test_create_document_success(client):
    with patch("src.routes.documents.client") as mock_client:
        # Suppose create_document returns the new doc ID
        mock_client.create_document.return_value = "abc123"
        payload = {"foo": "bar"}
        response = client.post("/documents", json=payload, headers={"X-API-Key": "test-key"})
        assert response.status_code == 201
        assert "id" in response.json
        assert response.json["id"] == "abc123"

def test_create_document_invalid_payload(client):
    # e.g., missing fields or invalid JSON
    response = client.post("/documents", data="not-a-json", headers={"X-API-Key": "test-key"})
    assert response.status_code == 400
    assert response.json["status"] == "error"
    assert "invalid" in response.json["message"].lower()
def test_update_document_not_found(client):
    with patch("src.routes.documents.client") as mock_client:
        mock_client.update_document.return_value = False
        payload = {"field": "new_value"}
        response = client.put("/documents/1", json=payload, headers={"X-API-Key": "test-key"})
        assert response.status_code == 404
        assert response.json["status"] == "error"

def test_delete_document_not_found(client):
    with patch("src.routes.documents.client") as mock_client:
        mock_client.delete_document.return_value = False
        response = client.delete("/documents/1", headers={"X-API-Key": "test-key"})
        assert response.status_code == 404
        assert response.json["status"] == "error"

def test_list_documents_empty(client):
    with patch("src.routes.documents.client") as mock_client:
        mock_client.list_documents.return_value = []
        response = client.get("/documents", headers={"X-API-Key": "test-key"})
        assert response.status_code == 200
        assert response.json == []
