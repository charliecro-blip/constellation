from constellation_core.chart import calculate_chart
from constellation_core.schemas import BirthData


def test_calculate_chart_smoke_known_time():
    birth = BirthData(
        name="Smoke Test",
        date="1992-01-03",
        time="17:37",
        time_known=True,
        latitude=29.4252,
        longitude=-98.4946,
        timezone="America/Chicago",
    )
    chart = calculate_chart(birth)
    assert "sun" in chart.placements
    assert "moon" in chart.placements
    assert "ascendant" in chart.angles
    assert "midheaven" in chart.angles
    assert chart.placements["sun"].sign == "Capricorn"


def test_calculate_chart_smoke_unknown_time():
    birth = BirthData(
        name="Unknown Time",
        date="1992-01-03",
        time=None,
        time_known=False,
        latitude=29.4252,
        longitude=-98.4946,
        timezone="America/Chicago",
    )
    chart = calculate_chart(birth)
    assert "sun" in chart.placements
    assert chart.angles == {}
    assert chart.houses is None
    assert chart.warnings
