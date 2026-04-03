from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_resources_returns_200():
    response = client.get("/admin/resources")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_post_resource_success():
    payload = {
        "id": "rs-test-001",
        "title": "Test Resource",
        "resource_type": "pdf",
        "status": "published"
    }

    response = client.post("/admin/resources", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["id"] == payload["id"]
    assert body["title"] == payload["title"]
    assert body["resource_type"] == payload["resource_type"]
    assert body["status"] == payload["status"]


def test_post_resource_validation_failure():
    payload = {
        "id": "rs-test-002",
        "title": "Bad Resource",
        "resource_type": "pdf",
        "status": "wrong-status"
    }

    response = client.post("/admin/resources", json=payload)
    assert response.status_code == 422