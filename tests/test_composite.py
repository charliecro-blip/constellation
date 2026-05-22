from constellation_core.composite import calculate_midpoint_composite
from constellation_core.schemas import BirthData
from constellation_core.chart import calculate_chart


def test_midpoint_composite_contains_core_planets():
    a = calculate_chart(BirthData(
        name="A",
        date="1992-01-03",
        time="17:37",
        time_known=True,
        latitude=29.4252,
        longitude=-98.4946,
        timezone="America/Chicago",
    ))
    b = calculate_chart(BirthData(
        name="B",
        date="1990-07-15",
        time="09:15",
        time_known=True,
        latitude=40.7128,
        longitude=-74.0060,
        timezone="America/New_York",
    ))

    composite = calculate_midpoint_composite(a, b)

    assert "sun" in composite.placements
    assert "moon" in composite.placements
    assert "venus" in composite.placements
    assert composite.angles == {}
    assert composite.houses is None
    assert composite.warnings
