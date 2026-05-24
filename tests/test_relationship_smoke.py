from constellation_core.relationship import calculate_relationship
from constellation_core.schemas import BirthData


def test_calculate_relationship_smoke():
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

    assert relationship.person_a.name == "Person A"
    assert relationship.person_a.house_system == "placidus"
    assert relationship.person_b.name == "Person B"
    assert relationship.composite is not None
    assert "sun" in relationship.composite.placements
    assert isinstance(relationship.synastry_aspects, list)
    assert isinstance(relationship.house_overlays, list)
    assert relationship.house_overlays
    assert isinstance(relationship.composite_aspects, list)
