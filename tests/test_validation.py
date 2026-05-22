from constellation_core.validation import ExpectedPoint, ValidationFixture, validate_chart_against_fixture
from constellation_core.chart import calculate_chart
from constellation_core.schemas import BirthData


def test_validation_passes_for_sun_sign():
    birth = BirthData(
        name="Validation Test",
        date="1992-01-03",
        time="17:37",
        time_known=True,
        latitude=29.4252,
        longitude=-98.4946,
        timezone="America/Chicago",
    )
    chart = calculate_chart(birth)
    fixture = ValidationFixture(
        birth=birth,
        expected={"sun": ExpectedPoint(sign="Capricorn", tolerance=1.0)},
        source="test",
    )
    results = validate_chart_against_fixture(chart, fixture)
    assert len(results) == 1
    assert results[0].passed


def test_validation_fails_for_missing_point():
    birth = BirthData(
        name="Validation Test",
        date="1992-01-03",
        time="17:37",
        time_known=True,
        latitude=29.4252,
        longitude=-98.4946,
        timezone="America/Chicago",
    )
    chart = calculate_chart(birth)
    fixture = ValidationFixture(
        birth=birth,
        expected={"not_a_point": ExpectedPoint(sign="Capricorn")},
        source="test",
    )
    results = validate_chart_against_fixture(chart, fixture)
    assert len(results) == 1
    assert not results[0].passed
