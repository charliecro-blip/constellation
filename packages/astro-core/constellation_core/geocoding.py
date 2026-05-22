"""Geocoding adapter layer.

The prototype can work without a geocoding provider. When a GEOCODING_API_KEY is
available, this module can use Geoapify-compatible search. Otherwise it falls
back to built-in presets and clear provider_unavailable messaging.
"""

from __future__ import annotations

import json
import os
from urllib.parse import urlencode
from urllib.request import urlopen

from pydantic import BaseModel, Field
from timezonefinder import TimezoneFinder

from .places import PlacePreset, list_place_presets


class ResolvedPlace(BaseModel):
    label: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str
    source: str
    confidence: str = "medium"


class PlaceSearchResponse(BaseModel):
    query: str
    results: list[ResolvedPlace]
    provider: str
    provider_available: bool
    message: str | None = None


_TIMEZONE_FINDER = TimezoneFinder()


def timezone_for_coordinates(latitude: float, longitude: float) -> str:
    timezone = _TIMEZONE_FINDER.timezone_at(lat=latitude, lng=longitude)
    return timezone or "UTC"


def _preset_to_resolved(preset: PlacePreset) -> ResolvedPlace:
    return ResolvedPlace(
        label=preset.label,
        latitude=preset.latitude,
        longitude=preset.longitude,
        timezone=preset.timezone,
        source="preset",
        confidence="medium",
    )


def search_place_presets(query: str) -> list[ResolvedPlace]:
    normalized = query.strip().lower()
    if not normalized:
        return []
    matches = []
    for preset in list_place_presets():
        if normalized in preset.label.lower() or normalized in preset.id.lower():
            matches.append(_preset_to_resolved(preset))
    return matches


def search_geoapify(query: str, api_key: str, limit: int = 5) -> list[ResolvedPlace]:
    params = urlencode({"text": query, "limit": limit, "apiKey": api_key})
    url = f"https://api.geoapify.com/v1/geocode/search?{params}"
    with urlopen(url, timeout=8) as response:
        payload = json.loads(response.read().decode("utf-8"))

    results: list[ResolvedPlace] = []
    for feature in payload.get("features", []):
        properties = feature.get("properties", {})
        latitude = properties.get("lat")
        longitude = properties.get("lon")
        if latitude is None or longitude is None:
            coordinates = feature.get("geometry", {}).get("coordinates", [])
            if len(coordinates) >= 2:
                longitude, latitude = coordinates[0], coordinates[1]
        if latitude is None or longitude is None:
            continue

        formatted = properties.get("formatted") or properties.get("address_line1") or query
        timezone = timezone_for_coordinates(float(latitude), float(longitude))
        results.append(ResolvedPlace(
            label=formatted,
            latitude=float(latitude),
            longitude=float(longitude),
            timezone=timezone,
            source="geoapify",
            confidence="high",
        ))
    return results


def search_places(query: str) -> PlaceSearchResponse:
    api_key = os.getenv("GEOCODING_API_KEY") or os.getenv("GEOAPIFY_API_KEY")
    if api_key:
        try:
            results = search_geoapify(query, api_key=api_key)
            if results:
                return PlaceSearchResponse(
                    query=query,
                    results=results,
                    provider="geoapify",
                    provider_available=True,
                )
        except Exception as exc:  # pragma: no cover - network failure path
            preset_results = search_place_presets(query)
            return PlaceSearchResponse(
                query=query,
                results=preset_results,
                provider="geoapify",
                provider_available=False,
                message=f"Geocoding provider failed; returned preset matches instead. Error: {exc}",
            )

    preset_results = search_place_presets(query)
    return PlaceSearchResponse(
        query=query,
        results=preset_results,
        provider="presets",
        provider_available=False,
        message="No geocoding API key configured; returned built-in preset matches only.",
    )
