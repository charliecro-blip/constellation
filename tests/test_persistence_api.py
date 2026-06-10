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
