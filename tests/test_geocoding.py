from constellation_core.geocoding import search_place_presets, search_places, timezone_for_coordinates


def test_place_preset_search_finds_austin():
    results = search_place_presets("Austin")
    assert results
    assert results[0].label == "Austin, TX"
    assert results[0].timezone == "America/Chicago"


def test_search_places_without_provider_uses_presets(monkeypatch):
    monkeypatch.delenv("GEOAPIFY_API_KEY", raising=False)
    monkeypatch.delenv("GEOCODING_API_KEY", raising=False)

    response = search_places("New York")

    assert response.provider == "presets"
    assert not response.provider_available
    assert response.results
    assert response.results[0].timezone == "America/New_York"


def test_timezone_for_coordinates():
    timezone = timezone_for_coordinates(30.2672, -97.7431)
    assert timezone == "America/Chicago"
