from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_admin_returns_200():
    response = client.get("/admin")
    assert response.status_code == 200


def test_admin_response_shape():
    response = client.get("/admin")
    body = response.json()

    assert body["service"] == "cms-monolith"
    assert body["status"] == "ready"
    assert body["domains"] == ["exercises", "content", "resources"]