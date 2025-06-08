import pytest


from app import create_app   # ← This is where pytest was failing

# ---- Test Objective 1: Health Endpoint ----

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["API_KEYS"] = ["test-key"]
    with app.test_client() as client:
        yield client

def test_health_route(client):
    """
    Test that the /health endpoint returns 200 and the expected JSON structure.
    """
    response = client.get("/health")
    assert response.status_code == 200
    # Match your actual implementation's response:
    assert response.json == {"message": "Service is healthy.", "status": "success"}

def test_health_route_without_api_key(tmp_path):
    # Create a fresh client without injecting any API_KEYS config
    app = create_app()
    app.config["TESTING"] = True
    # Do NOT set app.config["API_KEYS"]
    with app.test_client() as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json == {"message": "Service is healthy.", "status": "success"}
