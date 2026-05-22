from constellation_core.report import generate_report_from_birth_data
from constellation_core.schemas import BirthData


def test_generate_report_markdown_contains_core_sections():
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

    report = generate_report_from_birth_data(person_a, person_b)
    markdown = report.to_markdown()

    assert "Relationship Field Map" in markdown
    assert "Top Detected Patterns" in markdown
    assert "Early Interpretation Layer" in markdown
    assert "The Field Between You" in markdown
    assert "Composite Sun" in markdown
    assert "Composite Moon" in markdown
