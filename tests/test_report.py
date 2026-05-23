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
    assert "Relationship Map Summary" in markdown
    required_sections = [
        "Relationship Map Summary",
        "Most Important Signatures",
        "Synastry: How You Activate Each Other",
        "House Overlays: Where Each Person Lands",
        "Composite: The Field Between You",
        "Friction / Repair Themes",
        "Optional Technical Details",
    ]
    for section in required_sections:
        assert section in markdown
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
    assert "Origin story / symbolic context" in markdown
    assert "Technical report details" in markdown


def test_generate_report_includes_collapsed_technical_metadata_and_names():
    context = RelationshipContext(relationship_type="friend", status="current")
    report = generate_report_from_birth_data(_person_a(), _person_b(), context=context)
    markdown = report.to_markdown()

    assert "<details><summary>Technical report details</summary>" in markdown
    assert "Generated at (UTC):" in markdown
    assert "House system:" in markdown
    assert "Prototype output: yes" in markdown
    assert "Person A: Person A" in markdown
    assert "Person B: Person B" in markdown
    assert "Relationship type: friend" in markdown
    assert "person_a" not in markdown
    assert "person_b" not in markdown
