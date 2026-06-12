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
    assert (
        "Map the people who shape your life through astrology, timing, and relational patterning."
        in response.text
    )
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


def test_chart_endpoint_defaults_to_placidus():
    response = client.post("/chart", json=PERSON_A)
    assert response.status_code == 200
    payload = response.json()
    assert payload["house_system"] == "placidus"
    assert payload["houses"]["system"] == "placidus"
    assert payload["placements"]["sun"]["sign"] == "Capricorn"
    assert "ascendant" in payload["angles"]


def test_chart_endpoint_keeps_whole_sign_selectable():
    response = client.post("/chart?house_system=whole_sign", json=PERSON_A)
    assert response.status_code == 200
    payload = response.json()
    assert payload["house_system"] == "whole_sign"
    assert payload["houses"]["system"] == "whole_sign"


def test_relationship_endpoint():
    response = client.post(
        "/relationship",
        json={
            "person_a": PERSON_A,
            "person_b": PERSON_B,
            "house_system": "whole_sign",
            "context": {
                "relationship_type": "romantic",
                "status": "current",
                "user_question": "What is this dynamic?",
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "calculation" in payload
    assert "patterns" in payload
    assert payload["calculation"]["composite"] is not None
    assert payload["calculation"]["person_a"]["house_system"] == "whole_sign"


def test_report_endpoint():
    response = client.post(
        "/report",
        json={
            "person_a": PERSON_A,
            "person_b": PERSON_B,
            "house_system": "whole_sign",
            "context": {
                "relationship_type": "romantic",
                "status": "current",
                "origin_story": "We met unexpectedly.",
            },
        },
    )
    assert response.status_code == 200
    markdown = response.json()["markdown"]
    assert "Relationship Field Map" in markdown
    assert "Overview" in markdown
    assert "How Person A Activates Person B" in markdown
    assert "How Person B Activates Person A" in markdown
    assert "Composite Field" in markdown
    assert "Friction and Repair" in markdown
    assert "Calculated chart check" in markdown
    assert "Ascendant:" in markdown
    assert "Sun: Capricorn" in markdown
    assert "House system: Whole Sign" in markdown
    assert "Context Notes" in markdown
    assert "Origin note" in markdown
    assert "Technical report details" not in markdown


def test_report_enhance_unavailable_without_openai_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post("/report/enhance", json={"markdown": "# Relationship Field Map"})

    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]


def test_report_enhance_validates_markdown_is_provided(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    response = client.post("/report/enhance", json={"markdown": "   "})

    assert response.status_code == 422
    assert "markdown is required" in response.json()["detail"]


def test_report_enhance_returns_markdown_shape(monkeypatch):
    from constellation_core import api

    def fake_enhance(request):
        assert request.markdown == "# Relationship Field Map\n\n## Overview\nStandard report."
        assert request.context.relationship_type == "ex"
        return "# Relationship Field Map\n\n## Overview\nEnhanced report."

    monkeypatch.setattr(api, "enhance_report_markdown", fake_enhance)

    response = client.post(
        "/report/enhance",
        json={
            "markdown": "# Relationship Field Map\n\n## Overview\nStandard report.",
            "context": {"relationship_type": "ex", "status": "past"},
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "markdown": "# Relationship Field Map\n\n## Overview\nEnhanced report."
    }


def test_report_enhance_provider_exception_returns_safe_502(monkeypatch):
    from constellation_core import api
    from constellation_core.ai_enhancement import (
        EnhancementProviderError,
        PROVIDER_ERROR_MESSAGE,
    )

    secret_key = "sk-test-secret-key"

    def fake_enhance(request):
        raise EnhancementProviderError(PROVIDER_ERROR_MESSAGE) from RuntimeError(
            f"upstream leaked {secret_key}"
        )

    monkeypatch.setattr(api, "enhance_report_markdown", fake_enhance)

    response = client.post("/report/enhance", json={"markdown": "# Relationship Field Map"})

    assert response.status_code == 502
    detail = response.json()["detail"]
    assert detail == PROVIDER_ERROR_MESSAGE
    assert secret_key not in detail
    assert "RuntimeError" not in detail


def test_report_enhance_prompt_guardrails():
    from constellation_core.ai_enhancement import AI_ENHANCEMENT_SYSTEM_PROMPT

    prompt = AI_ENHANCEMENT_SYSTEM_PROMPT.lower()
    assert "do not invent placements" in prompt
    assert "keep the same main section headings" in prompt
    assert "do not invent astrology" in prompt
    assert "do not introduce new aspects" in prompt
    assert "preserve the deterministic priorities" in prompt
    assert "do not turn the report into compatibility scoring" in prompt
    assert "fate, soulmate, twin flame, destiny" in prompt
    assert "do not add compatibility scores" in prompt
    assert "meant to be" in prompt
    assert "do not use raw orb numbers" in prompt
    assert "return only markdown" in prompt
    assert "preserve astrology facts and section headings" in prompt
    assert "rewrite the prose substantially" in prompt
    assert "additional" in prompt
    assert "central" in prompt
    assert "moderate" in prompt
    assert "exact" in prompt
    assert "very close" in prompt
    assert "close" in prompt
    assert "supporting texture" in prompt
    assert "the ascendant/descendant axis describes" in prompt
    assert "the listed bodies operate less like separate details" in prompt
    assert "the planet person may appear as" in prompt
    assert "provide a baseline" in prompt
    assert "unique entity" in prompt
    assert "thrives on" in prompt
    assert "navigate the complexities" in prompt
    assert "fosters" in prompt
    assert "invites both" in prompt
    assert "highlights" in prompt
    assert "suggests" in prompt
    assert "journey" in prompt
    assert "concrete relational language" in prompt
    assert "theme → felt experience → shadow → repair → agency" in prompt
    assert "fewer, deeper themes" in prompt
    assert "first overview paragraph" in prompt
    assert "do not over-soften difficult dynamics" in prompt
    assert "precise, warm, and human" in prompt


def test_report_endpoint_defaults_to_placidus_when_omitted():
    response = client.post(
        "/report",
        json={
            "person_a": PERSON_A,
            "person_b": PERSON_B,
            "context": {"relationship_type": "romantic", "status": "current"},
        },
    )

    assert response.status_code == 200
    markdown = response.json()["markdown"]
    assert "House system: Placidus" in markdown


def test_saved_relationship_preserves_selected_house_system_in_report():
    from constellation_core.database import init_db

    init_db()
    res_a = client.post(
        "/birth-profiles",
        json={
            "display_name": "Saved A",
            "birth_date": "1992-01-03",
            "birth_time": "17:37:00",
            "time_known": True,
            "latitude": 29.4252,
            "longitude": -98.4946,
            "timezone": "America/Chicago",
            "birthplace_label": "San Antonio, TX",
        },
    )
    res_b = client.post(
        "/birth-profiles",
        json={
            "display_name": "Saved B",
            "birth_date": "1990-07-15",
            "birth_time": "09:15:00",
            "time_known": True,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timezone": "America/New_York",
            "birthplace_label": "New York, NY",
        },
    )
    rel = client.post(
        "/saved-relationships",
        json={
            "person_a_id": res_a.json()["id"],
            "person_b_id": res_b.json()["id"],
            "relationship_type": "romantic",
            "status": "current",
            "house_system": "whole_sign",
        },
    )

    assert rel.status_code == 200
    assert rel.json()["house_system"] == "whole_sign"
    report = client.post(f"/saved-relationships/{rel.json()['id']}/report")
    assert report.status_code == 200
    assert "House system: Whole Sign" in report.json()["markdown"]
    assert "Birthplace: San Antonio, TX" in report.json()["markdown"]
