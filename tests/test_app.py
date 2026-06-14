import copy

import pytest
from fastapi.testclient import TestClient
import src.app as app_module

client = TestClient(app_module.app)

original_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities = copy.deepcopy(original_activities)
    return app_module.activities


def test_get_activities_returns_activity_data():
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    email = "test@example.com"
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]


def test_signup_fails_for_duplicate_email():
    email = "test@example.com"
    first = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert first.status_code == 200

    duplicate = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Student already signed up"


def test_remove_participant_deletes_email():
    email = "test@example.com"
    signup = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert signup.status_code == 200

    response = client.delete("/activities/Chess%20Club/participants", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"

    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_404():
    response = client.delete("/activities/Chess%20Club/participants", params={"email": "noone@example.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_missing_activity_returns_404_for_signup_and_delete():
    signup = client.post("/activities/NoSuchActivity/signup", params={"email": "test@example.com"})
    assert signup.status_code == 404
    assert signup.json()["detail"] == "Activity not found"

    delete = client.delete("/activities/NoSuchActivity/participants", params={"email": "test@example.com"})
    assert delete.status_code == 404
    assert delete.json()["detail"] == "Activity not found"
