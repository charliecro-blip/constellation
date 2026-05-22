# Geocoding and Timezone Plan

The current prototype accepts latitude, longitude, and IANA timezone directly. This is deliberate: chart calculation must be validated before adding place lookup.

## Why This Matters

Birthplace handling is one of the easiest places for astrology software to go wrong.

The system eventually needs to resolve:

1. User-entered place name
2. Latitude and longitude
3. Historical timezone at the birth date
4. Daylight saving time where applicable
5. UTC conversion

If any of these are wrong, the Moon, Ascendant, Midheaven, houses, and house overlays can be wrong.

## MVP Strategy

### Stage 1 — Manual Coordinates / Timezone
Current stage.

The user or fixture provides:
- latitude
- longitude
- timezone

This lets us validate the ephemeris pipeline without API dependency.

### Stage 2 — Place Lookup Adapter
Add a provider interface:

```python
class PlaceResolver:
    def resolve(place_query: str) -> ResolvedPlace:
        ...
```

Return:
- canonical place name
- latitude
- longitude
- country / region metadata if available

Candidate providers:
- Google Maps
- Mapbox
- Geoapify
- Nominatim / OpenStreetMap

### Stage 3 — Historical Timezone Adapter
Add a timezone resolver:

```python
class TimezoneResolver:
    def resolve(latitude: float, longitude: float, birth_date: str) -> str:
        ...
```

Candidate tools:
- timezonefinder for timezone name by coordinates
- Python zoneinfo for DST and historical UTC conversion
- external APIs only if local libraries prove insufficient

### Stage 4 — User-Facing Confidence
Every calculated chart should retain:
- input place string
- resolved place name
- latitude / longitude
- timezone
- UTC datetime
- confidence warnings

## Open Questions

1. Which geocoding provider gives best balance of reliability, cost, and ease?
2. Do we need fuzzy search / autocomplete in MVP?
3. Should we store place lookups locally to avoid repeated API calls?
4. What is the fallback when a place name is ambiguous?

## Recommendation

Do not add paid geocoding until calculation has been validated with known charts.

Next practical step:
- add schemas for resolved places
- keep API-provider implementation abstract
- use manual coordinates for validation fixtures
