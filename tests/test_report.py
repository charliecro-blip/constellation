from constellation_core.context import RelationshipContext
from constellation_core.report import generate_relationship_report, generate_report_from_birth_data
from constellation_core.schemas import Aspect, BirthData, Chart, RelationshipCalculation


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


def test_generate_report_markdown_contains_polished_sections_without_technical_details():
    report = generate_report_from_birth_data(_person_a(), _person_b())
    markdown = report.to_markdown()

    assert "Relationship Field Map" in markdown
    required_sections = [
        "Central Signatures",
        "Supporting Patterns",
        "Composite Field",
        "Friction and Repair",
    ]
    for section in required_sections:
        assert section in markdown
    assert "Relationship Map Summary" not in markdown
    assert "Optional Technical Details" not in markdown
    assert "Prototype output" not in markdown
    assert "Generated at (UTC):" not in markdown
    assert "orb " not in markdown.lower()
    assert "Gift:" not in markdown
    assert "Care point:" not in markdown


def test_generate_report_includes_context_notes_without_debug_metadata():
    context = RelationshipContext(
        relationship_type="romantic",
        status="current",
        user_question="What is the dynamic?",
        origin_story="We met unexpectedly and the connection felt vivid.",
        known_themes=["attraction", "communication"],
    )
    report = generate_report_from_birth_data(_person_a(), _person_b(), context=context)
    markdown = report.to_markdown()

    assert "Context Notes" in markdown
    assert "Question in the room: What is the dynamic?" in markdown
    assert "Origin note: We met unexpectedly and the connection felt vivid." in markdown
    assert "Named themes: attraction, communication." in markdown
    assert "Technical report details" not in markdown
    assert "Relationship type:" not in markdown
    assert "Status:" not in markdown


def test_angle_luminary_signature_leads_house_overlay():
    chart_a = Chart(
        name="Charlie",
        birth=_person_a().model_copy(update={"name": "Charlie"}),
        julian_day_ut=None,
        house_system="whole_sign",
        placements={},
    )
    chart_b = Chart(
        name="Tess",
        birth=_person_b().model_copy(update={"name": "Tess"}),
        julian_day_ut=None,
        house_system="whole_sign",
        placements={},
    )
    relationship = RelationshipCalculation(
        person_a=chart_a,
        person_b=chart_b,
        synastry_aspects=[
            Aspect(point_a="ascendant", point_b="moon", aspect="conjunction", exact_angle=0, orb=0.4),
            Aspect(point_a="ascendant", point_b="venus", aspect="square", exact_angle=90, orb=0.8),
            Aspect(point_a="sun", point_b="moon", aspect="opposition", exact_angle=180, orb=0.6),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )

    markdown = generate_relationship_report(relationship).to_markdown()
    central = markdown.split("## Central Signatures")[1].split("## Supporting Patterns")[0]

    assert "Charlie's Ascendant conjunct Tess's Moon" in central
    assert "Charlie’s Ascendant conjunct Tess’s Moon" not in central
    assert "Charlie's Ascendant square Tess's Venus" in central
    assert "Charlie's Sun opposite Tess's Moon" in central
    assert "contact" not in central.lower()


def test_top_signatures_are_limited_and_no_surface_engine_or_glossary_leakage():
    report = generate_report_from_birth_data(_person_a(), _person_b())
    markdown = report.to_markdown()
    central_block = markdown.split("## Central Signatures")[1].split("## Supporting Patterns")[0]
    assert central_block.count("\n### ") <= 5
    assert "Surface vs Engine" not in markdown
    assert "describes affection, attraction, aesthetics" not in markdown
