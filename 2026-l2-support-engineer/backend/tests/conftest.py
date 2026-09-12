import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth import SESSIONS
from app.limits import REQUESTS

@pytest.fixture
def client():
    SESSIONS.clear()
    REQUESTS.clear()
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client

@pytest.fixture
def headers(client):
    token = client.post("/api/login", json={"username": "servidor", "password": "acesso-demo-2026"}).json()["token"]
    return {"Authorization": f"Bearer {token}"}
