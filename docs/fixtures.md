# Fixtures

Fixtures are small JSON files used to test chart and relationship calculations.

## Birth Fixture

A birth fixture uses normalized birth data. Phase 0 and Phase 1 intentionally require coordinates and timezone directly.

```json
{
  "name": "Example Person",
  "date": "1992-01-03",
  "time": "17:37",
  "time_known": true,
  "latitude": 29.4252,
  "longitude": -98.4946,
  "timezone": "America/Chicago"
}
```

## Validation Fixture

A validation fixture can add expected positions from a trusted source.

```json
{
  "birth": {
    "name": "Example Person",
    "date": "1992-01-03",
    "time": "17:37",
    "time_known": true,
    "latitude": 29.4252,
    "longitude": -98.4946,
    "timezone": "America/Chicago"
  },
  "expected": {
    "sun": {"sign": "Capricorn", "degree": 12.0},
    "moon": {"sign": "Capricorn", "degree": 2.0},
    "ascendant": {"sign": "Cancer", "degree": 11.0},
    "midheaven": {"sign": "Pisces", "degree": 28.0}
  },
  "source": "Astro.com or Solar Fire"
}
```

## Validation Checklist

Compare generated output against a trusted chart source:

- Sun sign and degree
- Moon sign and degree
- Mercury, Venus, and Mars degrees
- Ascendant degree
- Midheaven degree
- House system used
- Timezone and daylight saving assumptions

If planets match but Ascendant/MC are off, the problem is probably birth time, timezone, coordinates, or house/angle calculation.

If Moon is off by more than expected, check timezone and UTC conversion first.

If all planets are off, check Julian day calculation or ephemeris mode.
