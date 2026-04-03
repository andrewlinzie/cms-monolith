from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_content_returns_200():
    response = client.get("/admin/content")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_post_content_success():
    payload = {
        "id": "ct-test-001",
        "title": "Test Content",
        "content_type": "article",
        "status": "draft"
    }

    response = client.post("/admin/content", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["id"] == payload["id"]
    assert body["title"] == payload["title"]
    assert body["content_type"] == payload["content_type"]
    assert body["status"] == payload["status"]


def test_post_content_validation_failure():
    payload = {
        "id": "ct-test-002",
        "title": "Bad Content",
        "content_type": "article",
        "status": "bad-status"
    }

    response = client.post("/admin/content", json=payload)
    assert response.status_code == 422