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


def test_index_serves_prototype_ui():
    response = client.get("/")
    assert response.status_code == 200
    assert "An observatory for all your human relationships." in response.text
    assert "Start with you" in response.text
    assert "Add someone to your constellation" in response.text
    assert ("Your Constellation" in response.text) or ("Constellation View" in response.text)
    assert "Relationship Map" in response.text
    assert "Search for the city where you were born." in response.text
    assert "coordinates manually" in response.text


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_geocoding_status_without_provider(monkeypatch):
    monkeypatch.delenv("GEOAPIFY_API_KEY", raising=False)
    monkeypatch.delenv("GEOCODING_API_KEY", raising=False)

    response = client.get("/geocoding/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "presets"
    assert payload["provider_configured"] is False


def test_places_endpoint():
    response = client.get("/places")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert any(place["label"] == "Austin, TX" for place in payload)


def test_places_search_endpoint_without_provider(monkeypatch):
    monkeypatch.delenv("GEOAPIFY_API_KEY", raising=False)
    monkeypatch.delenv("GEOCODING_API_KEY", raising=False)

    response = client.get("/places/search", params={"q": "Austin"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "presets"
    assert payload["provider_available"] is False
    assert payload["results"]
    assert payload["results"][0]["timezone"] == "America/Chicago"


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
    assert "Central Signatures" in markdown
    assert "Supporting Patterns" in markdown
    assert "Composite Field" in markdown
    assert "Friction and Repair" in markdown
    assert "Context Notes" in markdown
    assert "Origin note" in markdown
    assert "Technical report details" not in markdown
