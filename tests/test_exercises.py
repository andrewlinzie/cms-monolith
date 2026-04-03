from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_exercises_returns_200():
    response = client.get("/admin/exercises")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_post_exercise_success():
    payload = {
        "id": "ex-test-001",
        "title": "Test Exercise",
        "category": "focus",
        "status": "draft"
    }

    response = client.post("/admin/exercises", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["id"] == payload["id"]
    assert body["title"] == payload["title"]
    assert body["category"] == payload["category"]
    assert body["status"] == payload["status"]


def test_post_exercise_validation_failure():
    payload = {
        "id": "ex-test-002",
        "title": "Bad Exercise",
        "category": "focus",
        "status": "invalid-status"
    }

    response = client.post("/admin/exercises", json=payload)
    assert response.status_code == 422