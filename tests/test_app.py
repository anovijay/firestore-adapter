import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app


@pytest.fixture
def app(monkeypatch):
    from config import Config
    monkeypatch.setattr(Config, "API_KEYS", ["test-key"])
    monkeypatch.setattr(Config, "FIRESTORE_CREDENTIALS", "{}")

    class DummyClient:
        def __init__(self, *args, **kwargs):
            self.db = None

    import app as app_module
    monkeypatch.setattr(app_module, "FirestoreClient", DummyClient)
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_root(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'success'


def test_health(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'success'


def test_protected_requires_key(client):
    resp = client.get('/protected')
    assert resp.status_code == 401


def test_protected_success(client):
    resp = client.get('/protected', headers={'X-API-Key': 'test-key'})
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'success'
