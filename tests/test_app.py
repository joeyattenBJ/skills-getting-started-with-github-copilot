import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original = copy.deepcopy(activities)
    with TestClient(app) as test_client:
        yield test_client
    activities.clear()
    activities.update(original)


def test_root_redirects_to_static_index(client):
    # Arrange
    # No setup needed for the redirect route.

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data(client):
    # Arrange
    # The default in-memory activities are already populated.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_adds_student(client):
    # Arrange
    activities["Soccer Club"]["participants"] = []

    # Act
    response = client.post("/activities/Soccer%20Club/signup", params={"email": "newstudent@mergington.edu"})

    # Assert
    assert response.status_code == 200
    assert "newstudent@mergington.edu" in activities["Soccer Club"]["participants"]
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Soccer Club"


def test_signup_rejects_duplicate_student(client):
    # Arrange
    activities["Chess Club"]["participants"] = ["duplicate@mergington.edu"]

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": "duplicate@mergington.edu"})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_removes_student_from_activity(client):
    # Arrange
    activities["Basketball Club"]["participants"] = ["remove@mergington.edu"]

    # Act
    response = client.delete("/activities/Basketball%20Club/participants/remove@mergington.edu")

    # Assert
    assert response.status_code == 200
    assert "remove@mergington.edu" not in activities["Basketball Club"]["participants"]
    assert response.json()["message"] == "Unregistered remove@mergington.edu from Basketball Club"
