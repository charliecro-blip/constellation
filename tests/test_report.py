from constellation_core.context import RelationshipContext
from constellation_core.report import generate_report_from_birth_data
from constellation_core.schemas import BirthData


def _person_a() -> BirthData:
    return BirthData(
        name="Person A",
        date="1992-01-03",
        time="17:37",
        time_known=True,
        latitude=29.4252,
        longitude=-98.4946,
        timezone="America/Chicago",
    )


def _person_b() -> BirthData:
    return BirthData(
        name="Person B",
        date="1990-07-15",
        time="09:15",
        time_known=True,
        latitude=40.7128,
        longitude=-74.0060,
        timezone="America/New_York",
    )


def test_generate_report_markdown_contains_core_sections():
    report = generate_report_from_birth_data(_person_a(), _person_b())
    markdown = report.to_markdown()

    assert "Relationship Field Map" in markdown
    assert "Context" in markdown
    assert "Top Detected Patterns" in markdown
    assert "Early Interpretation Layer" in markdown
    assert "The Field Between You" in markdown
    assert "Composite Sun" in markdown
    assert "Composite Moon" in markdown


def test_generate_report_includes_context_and_origin_story():
    context = RelationshipContext(
        relationship_type="romantic",
        status="current",
        user_question="What is the dynamic?",
        origin_story="We met unexpectedly and the connection felt vivid.",
        known_themes=["attraction", "communication"],
    )
    report = generate_report_from_birth_data(_person_a(), _person_b(), context=context)
    markdown = report.to_markdown()

    assert "Relationship type: romantic" in markdown
    assert "Status: current" in markdown
    assert "Origin story" in markdown
    assert "Biographical Activation" in markdown
    assert "not as decorative background" in markdown
