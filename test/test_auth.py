import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["API_KEYS"] = ["test-key"]
    with app.test_client() as client:
        yield client

def test_no_api_key(client):
    response = client.get('/protected')
    assert response.status_code == 401

def test_with_invalid_api_key(client):
    response = client.get('/protected', headers={"X-API-Key": "invalid-key"})
    assert response.status_code == 401

def test_with_valid_api_key(client):
    response = client.get('/protected', headers={"X-API-Key": "test-key"})
    assert response.status_code == 200
