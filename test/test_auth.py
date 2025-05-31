import pytest
from src.app import app  # <-- You need to add this line

@pytest.fixture
def client():
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
