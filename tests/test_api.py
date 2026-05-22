from fastapi.testclient import TestClient

from constellation_core.api import app


client = TestClient(app)


PERSON_A = {
    "name": "Person A",
    "date": "1992-01-03",
    "time": "17:37",
    "time_known": True,
    "latitude": 29.4252,
    "longitude": -98.4946,
    "timezone": "America/Chicago",
}

PERSON_B = {
    "name": "Person B",
    "date": "1990-07-15",
    "time": "09:15",
    "time_known": True,
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York",
}


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chart_endpoint():
    response = client.post("/chart", json=PERSON_A)
    assert response.status_code == 200
    payload = response.json()
    assert payload["placements"]["sun"]["sign"] == "Capricorn"
    assert "ascendant" in payload["angles"]


def test_relationship_endpoint():
    response = client.post("/relationship", json={
        "person_a": PERSON_A,
        "person_b": PERSON_B,
        "house_system": "whole_sign",
        "context": {
            "relationship_type": "romantic",
            "status": "current",
            "user_question": "What is this dynamic?",
        },
    })
    assert response.status_code == 200
    payload = response.json()
    assert "calculation" in payload
    assert "patterns" in payload
    assert payload["calculation"]["composite"] is not None


def test_report_endpoint():
    response = client.post("/report", json={
        "person_a": PERSON_A,
        "person_b": PERSON_B,
        "house_system": "whole_sign",
        "context": {
            "relationship_type": "romantic",
            "status": "current",
            "origin_story": "We met unexpectedly.",
        },
    })
    assert response.status_code == 200
    markdown = response.json()["markdown"]
    assert "Relationship Field Map" in markdown
    assert "Biographical Activation" in markdown
    assert "Origin story" in markdown
