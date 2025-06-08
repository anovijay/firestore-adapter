import pytest
from unittest.mock import patch, MagicMock
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['API_KEYS'] = ['test-key']
    with app.test_client() as client:
        yield client

def test_list_documents(client):
    with patch("routes.documents.get_client") as get_client:
        mock = MagicMock()
        mock.list_documents.return_value = [{"id": "1"}]
        get_client.return_value = mock
        response = client.get("/documents/mycoll", headers={"X-API-Key": "test-key"})
        assert response.status_code == 200
        assert response.json["status"] == "success"

def test_get_document_found(client):
    with patch("routes.documents.get_client") as get_client:
        mock = MagicMock()
        mock.read_document.return_value = {"id": "1", "field": "value"}
        get_client.return_value = mock
        response = client.get("/documents/mycoll/1", headers={"X-API-Key": "test-key"})
        assert response.status_code == 200
        assert response.json["status"] == "success"

def test_get_document_missing(client):
    with patch("routes.documents.get_client") as get_client:
        mock = MagicMock()
        mock.read_document.return_value = None
        get_client.return_value = mock
        response = client.get("/documents/mycoll/notfound", headers={"X-API-Key": "test-key"})
        assert response.status_code == 404

def test_add_document(client):
    with patch("routes.documents.get_client") as get_client:
        mock = MagicMock()
        mock.create_document.return_value = {"id": "2"}
        get_client.return_value = mock
        data = {"field": "value"}
        response = client.post("/documents/mycoll", json=data, headers={"X-API-Key": "test-key"})
        assert response.status_code == 200
        assert response.json["status"] == "success"

def test_update_document(client):
    with patch("routes.documents.get_client") as get_client:
        mock = MagicMock()
        mock.update_document.return_value = {"id": "1"}
        get_client.return_value = mock
        data = {"field": "new_value"}
        response = client.put("/documents/mycoll/1", json=data, headers={"X-API-Key": "test-key"})
        assert response.status_code == 200
        assert response.json["status"] == "success"

def test_delete_document(client):
    with patch("routes.documents.get_client") as get_client:
        mock = MagicMock()
        mock.delete_document.return_value = {"id": "1"}
        get_client.return_value = mock
        response = client.delete("/documents/mycoll/1", headers={"X-API-Key": "test-key"})
        assert response.status_code == 200
        assert response.json["status"] == "success"
def test_get_document_success(client):
    with patch("routes.documents.get_client") as get_client:
        mock = MagicMock()
        mock.read_document.return_value = {"id": "1", "field1": "value1"}
        get_client.return_value = mock
        response = client.get("/documents/mycoll/1", headers={"X-API-Key": "test-key"})
        assert response.status_code == 200
        assert response.json["status"] == "success"

def test_get_document_not_found(client):
    with patch("routes.documents.get_client") as get_client:
        mock = MagicMock()
        mock.read_document.return_value = None
        get_client.return_value = mock
        response = client.get("/documents/mycoll/1", headers={"X-API-Key": "test-key"})
        assert response.status_code == 404
        assert response.json["status"] == "error"
        assert "not found" in response.json["message"].lower()

def test_create_document_success(client):
    with patch("routes.documents.get_client") as get_client:
        mock = MagicMock()
        mock.create_document.return_value = {"id": "abc123"}
        get_client.return_value = mock
        payload = {"foo": "bar"}
        response = client.post("/documents/mycoll", json=payload, headers={"X-API-Key": "test-key"})
        assert response.status_code == 200
        assert response.json["status"] == "success"

def test_create_document_invalid_payload(client):
    # e.g., missing fields or invalid JSON
    response = client.post("/documents/mycoll", data="not-a-json", headers={"X-API-Key": "test-key"})
    assert response.status_code == 415
def test_update_document_not_found(client):
    with patch("routes.documents.get_client") as get_client:
        mock = MagicMock()
        mock.update_document.return_value = None
        get_client.return_value = mock
        payload = {"field": "new_value"}
        response = client.put("/documents/mycoll/1", json=payload, headers={"X-API-Key": "test-key"})
        assert response.status_code == 404
        assert response.json["status"] == "error"

def test_delete_document_not_found(client):
    with patch("routes.documents.get_client") as get_client:
        mock = MagicMock()
        mock.delete_document.return_value = None
        get_client.return_value = mock
        response = client.delete("/documents/mycoll/1", headers={"X-API-Key": "test-key"})
        assert response.status_code == 200
        assert response.json["status"] == "success"

def test_list_documents_empty(client):
    with patch("routes.documents.get_client") as get_client:
        mock = MagicMock()
        mock.list_documents.return_value = []
        get_client.return_value = mock
        response = client.get("/documents/mycoll", headers={"X-API-Key": "test-key"})
        assert response.status_code == 200
        assert response.json["status"] == "success"
