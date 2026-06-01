from constellation_core.patterns import detect_relationship_patterns
from constellation_core.relationship import calculate_relationship
from constellation_core.schemas import BirthData


def test_detect_relationship_patterns_returns_composite_moon_and_sun():
    person_a = BirthData(
        name="Person A",
        date="1992-01-03",
        time="17:37",
        time_known=True,
        latitude=29.4252,
        longitude=-98.4946,
        timezone="America/Chicago",
    )
    person_b = BirthData(
        name="Person B",
        date="1990-07-15",
        time="09:15",
        time_known=True,
        latitude=40.7128,
        longitude=-74.0060,
        timezone="America/New_York",
    )

    relationship = calculate_relationship(person_a, person_b)
    patterns = detect_relationship_patterns(relationship)
    assert any(pattern.layer == "composite" for pattern in patterns)
    assert any(pattern.id.startswith("composite_moon_") for pattern in patterns)
    assert any(pattern.id.startswith("composite_sun_") for pattern in patterns)
    assert patterns == sorted(patterns, key=lambda pattern: pattern.priority, reverse=True)
