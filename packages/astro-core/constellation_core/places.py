"""Small built-in place presets for the prototype UI.

This is not geocoding. It is a temporary convenience layer so testers do not
have to manually look up latitude, longitude, and timezone for common places.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PlacePreset(BaseModel):
    id: str
    label: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str


PLACE_PRESETS: list[PlacePreset] = [
    PlacePreset(id="san_antonio_tx", label="San Antonio, TX", latitude=29.4252, longitude=-98.4946, timezone="America/Chicago"),
    PlacePreset(id="austin_tx", label="Austin, TX", latitude=30.2672, longitude=-97.7431, timezone="America/Chicago"),
    PlacePreset(id="new_york_ny", label="New York, NY", latitude=40.7128, longitude=-74.0060, timezone="America/New_York"),
    PlacePreset(id="los_angeles_ca", label="Los Angeles, CA", latitude=34.0522, longitude=-118.2437, timezone="America/Los_Angeles"),
    PlacePreset(id="chicago_il", label="Chicago, IL", latitude=41.8781, longitude=-87.6298, timezone="America/Chicago"),
    PlacePreset(id="denver_co", label="Denver, CO", latitude=39.7392, longitude=-104.9903, timezone="America/Denver"),
    PlacePreset(id="seattle_wa", label="Seattle, WA", latitude=47.6062, longitude=-122.3321, timezone="America/Los_Angeles"),
    PlacePreset(id="portland_or", label="Portland, OR", latitude=45.5152, longitude=-122.6784, timezone="America/Los_Angeles"),
    PlacePreset(id="london_uk", label="London, UK", latitude=51.5074, longitude=-0.1278, timezone="Europe/London"),
    PlacePreset(id="paris_fr", label="Paris, France", latitude=48.8566, longitude=2.3522, timezone="Europe/Paris"),
    PlacePreset(id="berlin_de", label="Berlin, Germany", latitude=52.5200, longitude=13.4050, timezone="Europe/Berlin"),
    PlacePreset(id="sydney_au", label="Sydney, Australia", latitude=-33.8688, longitude=151.2093, timezone="Australia/Sydney"),
]


def list_place_presets() -> list[PlacePreset]:
    return PLACE_PRESETS


def find_place_preset(place_id: str) -> PlacePreset | None:
    for preset in PLACE_PRESETS:
        if preset.id == place_id:
            return preset
    return None
