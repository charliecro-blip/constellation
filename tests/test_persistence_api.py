import os
from importlib import reload

from fastapi.testclient import TestClient

import constellation_core.database as database
import constellation_core.api as api


def setup_module():
    os.environ["CONSTELLATION_DATABASE_URL"] = "sqlite:///./test_persistence.db"
    reload(database)
    reload(api)
    database.init_db()


def test_birth_profile_relationship_and_saved_report_flow():
    client = TestClient(api.app)

    person_a = {
        "display_name": "Person A",
        "birth_date": "1992-01-03",
        "birth_time": "17:37:00",
        "time_known": True,
        "latitude": 29.4252,
        "longitude": -98.4946,
        "timezone": "America/Chicago",
        "birthplace_label": "San Antonio, TX",
    }
    person_b = {
        "display_name": "Person B",
        "birth_date": "1990-07-15",
        "birth_time": "09:15:00",
        "time_known": True,
        "latitude": 40.7128,
        "longitude": -74.006,
        "timezone": "America/New_York",
        "birthplace_label": "New York, NY",
    }

    res_a = client.post("/birth-profiles", json=person_a)
    assert res_a.status_code == 200
    profile_a_id = res_a.json()["id"]

    res_b = client.post("/birth-profiles", json=person_b)
    assert res_b.status_code == 200
    profile_b_id = res_b.json()["id"]

    res_list = client.get("/birth-profiles")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 2

    rel = client.post("/saved-relationships", json={
        "person_a_id": profile_a_id,
        "person_b_id": profile_b_id,
        "relationship_type": "romantic",
        "status": "current",
        "known_themes": ["timing", "repair"],
        "house_system": "whole_sign",
        "origin_story": "We met unexpectedly.",
    })
    assert rel.status_code == 200
    assert rel.json()["house_system"] == "whole_sign"
    relationship_id = rel.json()["id"]

    report = client.post(f"/saved-relationships/{relationship_id}/report")
    assert report.status_code == 200
    markdown = report.json()["markdown"]
    assert "Relationship Field Map" in markdown
    assert "Overview" in markdown
    assert "Prototype output" not in markdown

    reports = client.get(f"/saved-relationships/{relationship_id}/reports")
    assert reports.status_code == 200
    assert len(reports.json()) >= 1


def test_saved_relationship_defaults_to_placidus():
    client = TestClient(api.app)
    res_a = client.post("/birth-profiles", json={
        "display_name": "Default A",
        "birth_date": "1992-01-03",
        "birth_time": "17:37:00",
        "time_known": True,
        "latitude": 29.4252,
        "longitude": -98.4946,
        "timezone": "America/Chicago",
    })
    res_b = client.post("/birth-profiles", json={
        "display_name": "Default B",
        "birth_date": "1990-07-15",
        "birth_time": "09:15:00",
        "time_known": True,
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York",
    })
    rel = client.post("/saved-relationships", json={
        "person_a_id": res_a.json()["id"],
        "person_b_id": res_b.json()["id"],
        "relationship_type": "romantic",
        "status": "current",
    })
    assert rel.status_code == 200
    assert rel.json()["house_system"] == "placidus"


def test_stateless_report_still_works():
    client = TestClient(api.app)
    response = client.post("/report", json={
        "person_a": {
            "name": "Person A",
            "date": "1992-01-03",
            "time": "17:37",
            "time_known": True,
            "latitude": 29.4252,
            "longitude": -98.4946,
            "timezone": "America/Chicago",
        },
        "person_b": {
            "name": "Person B",
            "date": "1990-07-15",
            "time": "09:15",
            "time_known": True,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timezone": "America/New_York",
        },
        "context": {"relationship_type": "romantic", "status": "current"},
    })
    assert response.status_code == 200
    assert "Relationship Field Map" in response.json()["markdown"]


def test_saved_report_creates_replaces_and_exposes_structured_motifs():
    client = TestClient(api.app)
    res_a = client.post("/birth-profiles", json={
        "display_name": "Motif A",
        "birth_date": "1992-01-03",
        "birth_time": "17:37:00",
        "time_known": True,
        "latitude": 29.4252,
        "longitude": -98.4946,
        "timezone": "America/Chicago",
    })
    res_b = client.post("/birth-profiles", json={
        "display_name": "Motif B",
        "birth_date": "1990-07-15",
        "birth_time": "09:15:00",
        "time_known": True,
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York",
    })
    rel = client.post("/saved-relationships", json={
        "person_a_id": res_a.json()["id"],
        "person_b_id": res_b.json()["id"],
        "relationship_type": "romantic",
        "status": "current",
    })
    relationship_id = rel.json()["id"]

    first_report = client.post(f"/saved-relationships/{relationship_id}/report")
    assert first_report.status_code == 200
    first_motifs = client.get(f"/saved-relationships/{relationship_id}/motifs")
    assert first_motifs.status_code == 200
    motifs_payload = first_motifs.json()
    assert 1 <= len(motifs_payload) <= 10
    assert all(item["relationship_id"] == relationship_id for item in motifs_payload)
    assert all(item["motif_key"] for item in motifs_payload)
    assert all("asteroid" not in item["motif_key"] for item in motifs_payload)
    assert any(item["lead_eligible"] for item in motifs_payload)

    second_report = client.post(f"/saved-relationships/{relationship_id}/report")
    assert second_report.status_code == 200
    second_motifs = client.get(f"/saved-relationships/{relationship_id}/motifs").json()
    assert len(second_motifs) == len(motifs_payload)
    identities = {(item["motif_key"], item["category"], item["layer"]) for item in second_motifs}
    assert len(identities) == len(second_motifs)


def test_motif_endpoint_404_for_missing_relationship():
    client = TestClient(api.app)
    response = client.get("/saved-relationships/not-a-real-id/motifs")
    assert response.status_code == 404


def _create_profile(client: TestClient, name: str, latitude: float, longitude: float, timezone: str, birthplace: str):
    response = client.post("/birth-profiles", json={
        "display_name": name,
        "birth_date": "1992-01-03" if name.endswith("A") else "1990-07-15",
        "birth_time": "17:37:00" if name.endswith("A") else "09:15:00",
        "time_known": True,
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "birthplace_label": birthplace,
    })
    assert response.status_code == 200
    return response.json()


def _create_saved_relationship(client: TestClient, name_prefix: str = "Flow"):
    person_a = _create_profile(client, f"{name_prefix} A", 29.4252, -98.4946, "America/Chicago", "San Antonio, TX")
    person_b = _create_profile(client, f"{name_prefix} B", 40.7128, -74.006, "America/New_York", "New York, NY")
    relationship = client.post("/saved-relationships", json={
        "person_a_id": person_a["id"],
        "person_b_id": person_b["id"],
        "relationship_type": "romantic",
        "status": "current",
        "user_question": "Original question",
        "origin_story": "Original story",
    })
    assert relationship.status_code == 200
    return relationship.json(), person_a, person_b


def test_saved_relationship_can_be_updated_and_regenerated_as_latest_report():
    client = TestClient(api.app)
    relationship, _, _ = _create_saved_relationship(client, "Update")

    update = client.patch(f"/saved-relationships/{relationship['id']}", json={
        "person_a": {
            "display_name": "Updated A",
            "birth_date": "1992-02-04",
            "birth_time": "06:15:00",
            "time_known": True,
            "latitude": 34.0522,
            "longitude": -118.2437,
            "timezone": "America/Los_Angeles",
            "birthplace_label": "Los Angeles, CA",
        },
        "person_b": {
            "display_name": "Updated B",
            "birth_date": "1990-08-16",
            "birth_time": None,
            "time_known": False,
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone": "Europe/London",
            "birthplace_label": "London, UK",
        },
        "relationship_type": "friend",
        "status": "current",
        "user_question": "Updated question",
        "origin_story": "Updated story",
        "known_themes": ["repair"],
        "house_system": "placidus",
    })
    assert update.status_code == 200
    assert update.json()["relationship_type"] == "friend"
    assert update.json()["user_question"] == "Updated question"

    person_a = client.get(f"/birth-profiles/{relationship['person_a_id']}")
    assert person_a.status_code == 200
    assert person_a.json()["display_name"] == "Updated A"
    assert person_a.json()["birthplace_label"] == "Los Angeles, CA"

    report = client.post(f"/saved-relationships/{relationship['id']}/report")
    assert report.status_code == 200
    assert "Updated question" in report.json()["markdown"]
    reports = client.get(f"/saved-relationships/{relationship['id']}/reports")
    assert reports.status_code == 200
    assert reports.json()[0]["id"] == report.json()["id"]


def test_regenerating_saved_relationship_replaces_motifs_instead_of_duplicating():
    client = TestClient(api.app)
    relationship, _, _ = _create_saved_relationship(client, "Replace")
    relationship_id = relationship["id"]

    first = client.post(f"/saved-relationships/{relationship_id}/report")
    assert first.status_code == 200
    first_motifs = client.get(f"/saved-relationships/{relationship_id}/motifs").json()
    second = client.post(f"/saved-relationships/{relationship_id}/report")
    assert second.status_code == 200
    second_motifs = client.get(f"/saved-relationships/{relationship_id}/motifs").json()

    assert len(second_motifs) == len(first_motifs)
    assert len({item["id"] for item in second_motifs}) == len(second_motifs)
    assert {item["relationship_id"] for item in second_motifs} == {relationship_id}


def test_deleting_saved_relationship_removes_reports_and_motifs_from_patterns():
    client = TestClient(api.app)
    relationship, _, _ = _create_saved_relationship(client, "Delete")
    relationship_id = relationship["id"]
    report = client.post(f"/saved-relationships/{relationship_id}/report")
    assert report.status_code == 200
    assert client.get(f"/saved-relationships/{relationship_id}/motifs").json()

    before_patterns = client.get("/constellation-patterns")
    assert before_patterns.status_code == 200
    assert relationship_id in str(before_patterns.json())

    deleted = client.delete(f"/saved-relationships/{relationship_id}")
    assert deleted.status_code == 200
    assert deleted.json()["status"] == "deleted"
    assert client.get(f"/saved-relationships/{relationship_id}").status_code == 404
    assert client.get(f"/saved-relationships/{relationship_id}/reports").status_code == 404
    assert client.get(f"/saved-relationships/{relationship_id}/motifs").status_code == 404

    after_patterns = client.get("/constellation-patterns")
    assert after_patterns.status_code == 200
    assert relationship_id not in str(after_patterns.json())


def test_report_feedback_persists_with_saved_relationship_and_can_be_fetched():
    client = TestClient(api.app)
    relationship, _, _ = _create_saved_relationship(client, "Feedback")
    report = client.post(f"/saved-relationships/{relationship['id']}/report")
    assert report.status_code == 200

    response = client.post("/report-feedback", json={
        "relationship_id": relationship["id"],
        "saved_report_id": report.json()["id"],
        "usefulness_rating": 5,
        "accuracy_rating": 4,
        "clarity_rating": 5,
        "felt_seen_rating": 4,
        "too_long": False,
        "too_intense": False,
        "too_technical": True,
        "what_landed": "The emotional recognition part landed.",
        "what_felt_off": "The Mars section felt like too much.",
        "central_theme_feedback": "Central theme was close.",
        "freeform_comment": "Keep the repair guidance practical.",
        "tester_label": "Tester A",
        "report_version_metadata": {"source": "pytest"},
    })
    assert response.status_code == 200
    payload = response.json()
    assert payload["feedback_id"]
    assert payload["relationship_id"] == relationship["id"]
    assert payload["saved_report_id"] == report.json()["id"]
    assert payload["clarity_rating"] == 5
    assert payload["report_version_metadata"] == {"source": "pytest"}

    fetched = client.get(f"/saved-relationships/{relationship['id']}/feedback")
    assert fetched.status_code == 200
    summary = fetched.json()
    assert summary["response_count"] == 1
    assert summary["average_clarity"] == 5
    assert summary["average_accuracy"] == 4
    assert summary["average_felt_seen"] == 4
    assert summary["most_recent"] == "Keep the repair guidance practical."
    assert summary["feedback"][0]["what_landed"] == "The emotional recognition part landed."


def test_report_feedback_rejects_invalid_relationship_or_report_ids():
    client = TestClient(api.app)
    missing_relationship = client.post("/report-feedback", json={
        "relationship_id": "not-a-real-relationship",
        "what_landed": "Something landed.",
    })
    assert missing_relationship.status_code == 404

    missing_report = client.post("/report-feedback", json={
        "saved_report_id": "not-a-real-report",
        "what_landed": "Something landed.",
    })
    assert missing_report.status_code == 404

    relationship_a, _, _ = _create_saved_relationship(client, "FeedbackA")
    relationship_b, _, _ = _create_saved_relationship(client, "FeedbackB")
    report_a = client.post(f"/saved-relationships/{relationship_a['id']}/report")
    assert report_a.status_code == 200
    mismatch = client.post("/report-feedback", json={
        "relationship_id": relationship_b["id"],
        "saved_report_id": report_a.json()["id"],
        "what_landed": "Something landed.",
    })
    assert mismatch.status_code == 422

    fetched_missing = client.get("/saved-relationships/not-a-real-relationship/feedback")
    assert fetched_missing.status_code == 404


def test_report_feedback_accepts_direct_unsaved_payload():
    client = TestClient(api.app)
    response = client.post("/report-feedback", json={
        "rating": 3,
        "clarity_rating": 4,
        "what_landed": "The tone was respectful.",
    })
    assert response.status_code == 200
    assert response.json()["relationship_id"] is None
    assert response.json()["saved_report_id"] is None
    assert response.json()["usefulness_rating"] == 3
