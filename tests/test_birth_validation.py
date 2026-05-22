import pytest
from pydantic import ValidationError

from constellation_core.schemas import BirthData


def _valid_payload() -> dict:
    return {
        "name": "Valid Person",
        "date": "1992-01-03",
        "time": "17:37",
        "time_known": True,
        "latitude": 29.4252,
        "longitude": -98.4946,
        "timezone": "America/Chicago",
    }


def test_birth_data_accepts_valid_payload():
    birth = BirthData(**_valid_payload())
    assert birth.date == "1992-01-03"
    assert birth.time == "17:37"


def test_birth_data_rejects_invalid_date():
    payload = _valid_payload()
    payload["date"] = "01/03/1992"
    with pytest.raises(ValidationError):
        BirthData(**payload)


def test_birth_data_rejects_invalid_time():
    payload = _valid_payload()
    payload["time"] = "25:99"
    with pytest.raises(ValidationError):
        BirthData(**payload)


def test_birth_data_rejects_invalid_latitude():
    payload = _valid_payload()
    payload["latitude"] = 100
    with pytest.raises(ValidationError):
        BirthData(**payload)


def test_birth_data_rejects_invalid_timezone():
    payload = _valid_payload()
    payload["timezone"] = "Not/AZone"
    with pytest.raises(ValidationError):
        BirthData(**payload)
