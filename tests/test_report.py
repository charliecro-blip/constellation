from constellation_core.context import RelationshipContext
from constellation_core.report import (
    build_report_diagnostics,
    build_report_synthesis_packet,
    generate_relationship_report,
    generate_report_from_birth_data,
)
from constellation_core.schemas import (
    Angle,
    Aspect,
    BirthData,
    Chart,
    HouseOverlay,
    Placement,
    RelationshipCalculation,
)


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
        "Overview",
        "Calculated chart check",
        "Person A Relationship Profile",
        "Person B Relationship Profile",
        "How Person A Activates Person B",
        "How Person B Activates Person A",
        "Composite Field",
        "Friction and Repair",
    ]
    for section in required_sections:
        assert section in markdown
    assert "Ascendant:" in markdown
    assert "Sun: Capricorn" in markdown
    assert "Moon:" in markdown
    assert "Venus:" in markdown
    assert "Mars:" in markdown
    assert "House system: Placidus" in markdown
    assert "Composite Sun/Moon/Ascendant baseline" not in markdown
    assert "provide a baseline" not in markdown.lower()
    assert "Relationship Map Summary" not in markdown
    assert "Optional Technical Details" not in markdown
    assert "Prototype output" not in markdown
    assert "Generated at (UTC):" not in markdown
    assert "Central Signatures" not in markdown.split("##", 2)[1]
    assert "orb " not in markdown.lower()
    banned_phrases = [
        "meant to be",
        "destined",
        "soulmate",
        "compatibility score",
        "twin flame",
        "navigate the complexities",
        "unique entity",
        "thrives on",
        "composite sun, moon, and ascendant provide a baseline",
    ]
    for phrase in banned_phrases:
        assert phrase not in markdown.lower()
    assert markdown.count("Look for these sign themes") <= 1
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
            Aspect(
                point_a="ascendant", point_b="moon", aspect="conjunction", exact_angle=0, orb=0.4
            ),
            Aspect(point_a="ascendant", point_b="venus", aspect="square", exact_angle=90, orb=0.8),
            Aspect(point_a="sun", point_b="moon", aspect="opposition", exact_angle=180, orb=0.6),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )

    markdown = generate_relationship_report(relationship).to_markdown()
    tess_to_charlie = markdown.split("## How Tess Activates Charlie")[1].split(
        "## Composite Field"
    )[0]
    charlie_to_tess = markdown.split("## How Charlie Activates Tess")[1].split(
        "## How Tess Activates Charlie"
    )[0]

    assert "Charlie's Ascendant conjunct Tess's Moon" in tess_to_charlie
    assert "Charlie’s Ascendant conjunct Tess’s Moon" not in tess_to_charlie
    assert "Charlie's Ascendant square Tess's Venus" in tess_to_charlie
    assert "Charlie's Sun opposite Tess's Moon" in charlie_to_tess
    assert "contact" not in tess_to_charlie.lower()


def test_top_signatures_are_limited_and_no_surface_engine_or_glossary_leakage():
    report = generate_report_from_birth_data(_person_a(), _person_b())
    markdown = report.to_markdown()
    directional_block = markdown.split("## How Person A Activates Person B")[1].split(
        "## How Person B Activates Person A"
    )[0]
    assert directional_block.count("\n### ") <= 5
    assert "Surface vs Engine" not in markdown
    assert "describes affection, attraction, aesthetics" not in markdown


def _synthetic_chart(name: str) -> Chart:
    return Chart(
        name=name,
        birth=_person_a().model_copy(update={"name": name}),
        julian_day_ut=None,
        house_system="whole_sign",
        placements={},
    )


def _placement(
    body: str, longitude: float, sign: str, degree: float | None = None, house: int | None = None
) -> Placement:
    return Placement(
        body=body,
        longitude=longitude,
        sign=sign,
        sign_index=int(longitude // 30),
        degree=degree if degree is not None else longitude % 30,
        house=house,
    )


def test_nodal_house_overlay_does_not_lead_or_show_background_label():
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("Charlie"),
        person_b=_synthetic_chart("Tess"),
        synastry_aspects=[
            Aspect(point_a="sun", point_b="moon", aspect="conjunction", exact_angle=0, orb=0.5)
        ],
        house_overlays=[
            HouseOverlay(
                planet_owner="person_a",
                house_owner="person_b",
                body="south_node",
                house=7,
                body_longitude=210,
            )
        ],
        composite=None,
        composite_aspects=[],
    )

    markdown = generate_relationship_report(relationship).to_markdown()
    overview = markdown.split("## Overview")[1].split("## Charlie Relationship Profile")[0]

    assert "South Node in Tess's 7th house" not in overview
    assert "Background." not in markdown


def test_composite_nodal_axis_on_mc_ic_is_central():
    composite = Chart(
        name="Composite",
        birth=_person_a().model_copy(update={"name": "Composite"}),
        julian_day_ut=None,
        house_system="synthetic",
        placements={
            "north_node": _placement("north_node", 90, "Cancer"),
            "south_node": _placement("south_node", 270, "Capricorn"),
            "sun": _placement("sun", 10, "Aries"),
            "moon": _placement("moon", 45, "Taurus"),
        },
        angles={
            "ascendant": Angle(name="Ascendant", longitude=0, sign="Aries", sign_index=0, degree=0),
            "midheaven": Angle(
                name="Midheaven", longitude=90, sign="Cancer", sign_index=3, degree=0
            ),
        },
    )
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("A"),
        person_b=_synthetic_chart("B"),
        synastry_aspects=[],
        house_overlays=[],
        composite=composite,
        composite_aspects=[],
    )

    markdown = generate_relationship_report(relationship).to_markdown()
    overview = markdown.split("## Overview")[1].split("## A Relationship Profile")[0]
    composite = markdown.split("## Composite Field")[1].split("## Friction and Repair")[0]

    assert "Composite nodal axis on MC/IC" in overview
    assert "Composite nodal axis on MC/IC" in composite


def test_composite_stellium_and_conjunction_cluster_detection_work():
    composite = Chart(
        name="Composite",
        birth=_person_a().model_copy(update={"name": "Composite"}),
        julian_day_ut=None,
        house_system="synthetic",
        placements={
            "sun": _placement("sun", 281, "Capricorn", 11),
            "venus": _placement("venus", 284, "Capricorn", 14),
            "ceres": _placement("ceres", 287, "Capricorn", 17),
            "mars": _placement("mars", 291, "Capricorn", 21),
            "moon": _placement("moon", 40, "Taurus", 10),
        },
    )
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("A"),
        person_b=_synthetic_chart("B"),
        synastry_aspects=[],
        house_overlays=[],
        composite=composite,
        composite_aspects=[],
    )

    markdown = generate_relationship_report(relationship).to_markdown()
    composite_block = markdown.split("## Composite Field")[1].split("## Friction and Repair")[0]

    assert "Composite Capricorn concentration" in composite_block
    assert "Composite conjunction cluster" in composite_block
    assert "Ceres" in composite_block


def test_composite_moon_uranus_progresses_from_concise_to_repair_language_without_duplicate_text():
    composite = Chart(
        name="Composite",
        birth=_person_a().model_copy(update={"name": "Composite"}),
        julian_day_ut=None,
        house_system="synthetic",
        placements={
            "sun": _placement("sun", 10, "Aries"),
            "moon": _placement("moon", 10, "Aries"),
            "uranus": _placement("uranus", 100, "Cancer"),
        },
    )
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("A"),
        person_b=_synthetic_chart("B"),
        synastry_aspects=[],
        house_overlays=[],
        composite=composite,
        composite_aspects=[
            Aspect(point_a="moon", point_b="uranus", aspect="square", exact_angle=90, orb=0.2)
        ],
    )

    markdown = generate_relationship_report(relationship).to_markdown()
    composite = markdown.split("## Composite Field")[1].split("## Friction and Repair")[0]
    friction = markdown.split("## Friction and Repair")[1]

    assert (
        "The relationship's emotional rhythm is electric, changeable, and hard to settle."
        in composite
    )
    assert "The Moon–Uranus square describes a rhythm problem" in friction
    assert composite.strip() != friction.strip()
    assert markdown.count("electric, changeable, and hard to settle") <= 2



def test_friction_and_repair_names_communication_heat_repair_move():
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("A"),
        person_b=_synthetic_chart("B"),
        synastry_aspects=[
            Aspect(point_a="mercury", point_b="mars", aspect="square", exact_angle=90, orb=0.1),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )

    markdown = generate_relationship_report(relationship).to_markdown()
    friction = markdown.split("## Friction and Repair")[1]

    assert "gap between intention" in friction
    assert "tone" in friction
    assert "impact" in friction
    assert "proof of incompatibility" in friction


def test_friction_and_repair_names_saturn_container_repair_move():
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("A"),
        person_b=_synthetic_chart("B"),
        synastry_aspects=[
            Aspect(point_a="moon", point_b="saturn", aspect="opposition", exact_angle=180, orb=0.2),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )

    markdown = generate_relationship_report(relationship).to_markdown()
    friction = markdown.split("## Friction and Repair")[1]

    assert "care and structure can coexist" in friction
    assert "supportive or restrictive" in friction
    assert "name expectations directly" in friction


def test_ai_enhancement_provider_exception_uses_safe_error_message():
    from types import SimpleNamespace

    import pytest

    from constellation_core.ai_enhancement import (
        EnhancementProviderError,
        PROVIDER_ERROR_MESSAGE,
        ReportEnhancementRequest,
        enhance_report_markdown,
    )

    secret_key = "sk-test-secret-key"

    class FakeCompletions:
        def create(self, **kwargs):
            raise RuntimeError(f"provider failed with key {secret_key} and payload {kwargs}")

    fake_client = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))

    with pytest.raises(EnhancementProviderError) as exc_info:
        enhance_report_markdown(
            ReportEnhancementRequest(markdown="# Relationship Field Map"),
            client=fake_client,
            api_key=secret_key,
        )

    message = str(exc_info.value)
    assert message == PROVIDER_ERROR_MESSAGE
    assert secret_key not in message
    assert "payload" not in message
    assert "RuntimeError" not in message


def test_ai_enhancement_uses_mock_openai_client_and_returns_markdown(monkeypatch):
    from types import SimpleNamespace

    from constellation_core.ai_enhancement import (
        AI_ENHANCEMENT_SYSTEM_PROMPT,
        ReportEnhancementContext,
        ReportEnhancementRequest,
        enhance_report_markdown,
    )

    captured = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="## Overview\nEnhanced."))]
            )

    fake_client = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))
    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    enhanced = enhance_report_markdown(
        ReportEnhancementRequest(
            markdown="# Relationship Field Map\n\n## Overview\nStandard.",
            context=ReportEnhancementContext(
                relationship_type="ex",
                status="past",
                user_question="What is the dynamic?",
                house_system="placidus",
            ),
        ),
        client=fake_client,
        api_key="test-key",
    )

    assert enhanced == "## Overview\nEnhanced."
    assert captured["model"] == "test-model"
    assert captured["messages"][0] == {"role": "system", "content": AI_ENHANCEMENT_SYSTEM_PROMPT}
    user_prompt = captured["messages"][1]["content"]
    assert "# Relationship Field Map" in user_prompt
    assert "Relationship type: ex" in user_prompt
    assert "House system: placidus" in user_prompt


def test_chart_check_includes_birthplace_and_unknown_time_qualification():
    known = _synthetic_chart("Known")
    known.birth = known.birth.model_copy(update={"birthplace_label": "San Antonio, TX"})
    known.placements = {
        "sun": _placement("sun", 280, "Capricorn", house=7),
        "moon": _placement("moon", 282, "Capricorn", house=7),
        "mercury": _placement("mercury", 260, "Sagittarius", house=6),
        "venus": _placement("venus", 255, "Sagittarius", house=6),
        "mars": _placement("mars", 250, "Sagittarius", house=6),
    }
    known.angles = {"ascendant": Angle(name="Ascendant", longitude=90, sign="Cancer", sign_index=3, degree=0)}
    unknown = _synthetic_chart("Unknown")
    unknown.birth = unknown.birth.model_copy(update={"time": None, "time_known": False})
    unknown.house_system = "placidus"
    unknown.placements = {"sun": _placement("sun", 160, "Virgo")}
    unknown.angles = {}
    relationship = RelationshipCalculation(
        person_a=known,
        person_b=unknown,
        synastry_aspects=[],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )

    markdown = generate_relationship_report(relationship).to_markdown()

    assert "## Calculated chart check" in markdown
    assert "- Ascendant: Cancer" in markdown
    assert "- Mercury: Sagittarius, 6th house" in markdown
    assert "- Birthplace: San Antonio, TX" in markdown
    assert "houses and Ascendant unavailable or approximate without a known birth time" in markdown


def test_mercury_mars_does_not_lead_romantic_report_over_luminary_signature():
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("Charlie"),
        person_b=_synthetic_chart("Ellis"),
        synastry_aspects=[
            Aspect(point_a="mars", point_b="mercury", aspect="square", exact_angle=90, orb=0.1),
            Aspect(point_a="sun", point_b="moon", aspect="conjunction", exact_angle=0, orb=2.0),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )
    context = RelationshipContext(relationship_type="romantic", status="current")

    overview = generate_relationship_report(relationship, context=context).to_markdown().split("## Overview")[1].split("## Calculated chart check")[0]

    assert "Charlie's Sun conjunct Ellis's Moon" in overview
    assert "Mars square Ellis's Mercury" not in overview.split(".", 1)[0]


def test_midheaven_contact_does_not_lead_romantic_report_without_contextual_repetition():
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("Charlie"),
        person_b=_synthetic_chart("Ellis"),
        synastry_aspects=[
            Aspect(point_a="midheaven", point_b="moon", aspect="conjunction", exact_angle=0, orb=0.1),
            Aspect(point_a="sun", point_b="moon", aspect="conjunction", exact_angle=0, orb=1.8),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )
    context = RelationshipContext(relationship_type="romantic", status="current")

    overview = generate_relationship_report(relationship, context=context).to_markdown().split("## Overview")[1].split("## Calculated chart check")[0]

    assert "Charlie's Sun conjunct Ellis's Moon" in overview
    assert "Midheaven" not in overview.split(".", 1)[0]

def _overview_block(markdown: str) -> str:
    return markdown.split("## Overview")[1].split("## Calculated chart check")[0]


def _first_overview_sentence(markdown: str) -> str:
    return _overview_block(markdown).strip().split(".", 1)[0]


def test_overview_opens_with_lead_eligible_theme_over_higher_mercury_mars():
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("A"),
        person_b=_synthetic_chart("B"),
        synastry_aspects=[
            Aspect(point_a="mercury", point_b="mars", aspect="square", exact_angle=90, orb=0.1),
            Aspect(point_a="moon", point_b="venus", aspect="trine", exact_angle=120, orb=1.5),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )
    context = RelationshipContext(relationship_type="romantic", status="current")

    markdown = generate_relationship_report(relationship, context=context).to_markdown()
    first_sentence = _first_overview_sentence(markdown)

    assert "Moon trine B's Venus" in first_sentence
    assert "Mercury square B's Mars" not in first_sentence
    assert "Mercury square B's Mars" in markdown


def test_isolated_mercury_mars_does_not_open_romantic_report():
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("A"),
        person_b=_synthetic_chart("B"),
        synastry_aspects=[
            Aspect(point_a="mercury", point_b="mars", aspect="square", exact_angle=90, orb=0.1),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )
    context = RelationshipContext(relationship_type="romantic", status="current")

    markdown = generate_relationship_report(relationship, context=context).to_markdown()

    assert "Mercury square B's Mars" not in _first_overview_sentence(markdown)
    assert "Mercury square B's Mars" in markdown


def test_mercury_mars_can_open_when_communication_context_is_requested():
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("A"),
        person_b=_synthetic_chart("B"),
        synastry_aspects=[
            Aspect(point_a="mercury", point_b="mars", aspect="square", exact_angle=90, orb=0.1),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )
    context = RelationshipContext(
        relationship_type="romantic",
        status="current",
        user_question="Why do communication and arguments escalate?",
    )

    markdown = generate_relationship_report(relationship, context=context).to_markdown()

    assert "Mercury square B's Mars" in _first_overview_sentence(markdown)


def test_isolated_public_life_signature_does_not_open_romantic_report():
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("A"),
        person_b=_synthetic_chart("B"),
        synastry_aspects=[
            Aspect(point_a="midheaven", point_b="moon", aspect="conjunction", exact_angle=0, orb=0.1),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )
    context = RelationshipContext(relationship_type="romantic", status="current")

    markdown = generate_relationship_report(relationship, context=context).to_markdown()

    assert "Midheaven conjunct B's Moon" not in _first_overview_sentence(markdown)


def test_public_life_signature_can_open_when_work_context_is_requested():
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("A"),
        person_b=_synthetic_chart("B"),
        synastry_aspects=[
            Aspect(point_a="midheaven", point_b="moon", aspect="conjunction", exact_angle=0, orb=0.1),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )
    context = RelationshipContext(
        relationship_type="romantic",
        status="current",
        user_question="Can this work as a professional collaboration or creative project?",
    )

    markdown = generate_relationship_report(relationship, context=context).to_markdown()

    assert "Midheaven conjunct B's Moon" in _first_overview_sentence(markdown)


def test_composite_only_generic_baseline_does_not_open_overview():
    composite = Chart(
        name="Composite",
        birth=_person_a().model_copy(update={"name": "Composite"}),
        julian_day_ut=None,
        house_system="synthetic",
        placements={
            "sun": _placement("sun", 10, "Aries"),
            "moon": _placement("moon", 50, "Taurus"),
        },
    )
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("A"),
        person_b=_synthetic_chart("B"),
        synastry_aspects=[],
        house_overlays=[],
        composite=composite,
        composite_aspects=[],
    )

    markdown = generate_relationship_report(relationship).to_markdown()
    overview = _overview_block(markdown)

    assert "Composite Sun" not in overview
    assert "Composite Moon" not in overview
    assert "baseline" not in overview.lower()
    assert "compatibility score" not in markdown.lower()
    assert "meant to be" not in markdown.lower()
    assert "destined" not in markdown.lower()


def test_direction_sections_are_limited_to_three_strongest_activations():
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("A"),
        person_b=_synthetic_chart("B"),
        synastry_aspects=[
            Aspect(point_a="sun", point_b="moon", aspect="conjunction", exact_angle=0, orb=0.5),
            Aspect(point_a="venus", point_b="mars", aspect="conjunction", exact_angle=0, orb=0.6),
            Aspect(point_a="venus", point_b="pluto", aspect="square", exact_angle=90, orb=0.7),
            Aspect(point_a="moon", point_b="saturn", aspect="opposition", exact_angle=180, orb=0.8),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )
    block = generate_relationship_report(relationship).to_markdown().split("## How A Activates B")[1].split("## How B Activates A")[0]
    assert block.count("\n### ") <= 3


def test_generic_composite_sun_moon_texture_is_omitted_without_specific_anchor():
    composite = Chart(
        name="Composite",
        birth=_person_a().model_copy(update={"name": "Composite"}),
        julian_day_ut=None,
        house_system="synthetic",
        placements={
            "sun": _placement("sun", 10, "Aries"),
            "moon": _placement("moon", 50, "Taurus"),
        },
    )
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("A"),
        person_b=_synthetic_chart("B"),
        synastry_aspects=[],
        house_overlays=[],
        composite=composite,
        composite_aspects=[],
    )
    composite_block = generate_relationship_report(relationship).to_markdown().split("## Composite Field")[1].split("## Friction and Repair")[0]
    assert "Composite Sun in" not in composite_block
    assert "Composite Moon in" not in composite_block
    assert "baseline" not in composite_block.lower()


def test_default_report_surfaces_only_tightly_relevant_mvp_asteroids():
    cases = [
        ("juno", "venus", "Juno"),
        ("chiron", "moon", "Chiron"),
        ("ceres", "mars", "Ceres"),
        ("vesta", "sun", "Vesta"),
    ]

    for asteroid, target, label in cases:
        relationship = RelationshipCalculation(
            person_a=_synthetic_chart("A"),
            person_b=_synthetic_chart("B"),
            synastry_aspects=[
                Aspect(point_a=asteroid, point_b=target, aspect="conjunction", exact_angle=0, orb=0.1),
            ],
            house_overlays=[],
            composite=None,
            composite_aspects=[],
        )

        markdown = generate_relationship_report(relationship).to_markdown()

        assert label in markdown

    weak_or_orphan_contacts = RelationshipCalculation(
        person_a=_synthetic_chart("A"),
        person_b=_synthetic_chart("B"),
        synastry_aspects=[
            Aspect(point_a="juno", point_b="mercury", aspect="conjunction", exact_angle=0, orb=0.1),
            Aspect(point_a="ceres", point_b="venus", aspect="conjunction", exact_angle=0, orb=2.1),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )
    markdown = generate_relationship_report(weak_or_orphan_contacts).to_markdown()

    assert "Juno conjunct B's Mercury" not in markdown
    assert "Ceres" not in markdown


def test_default_report_suppresses_advanced_asteroids_and_asteroid_to_asteroid_contacts():
    chart_a = _synthetic_chart("A").model_copy(
        update={
            "placements": {
                "eros": _placement("eros", 15, "Aries", house=7),
                "psyche": _placement("psyche", 16, "Aries", house=8),
                "lilith": _placement("lilith", 17, "Aries", house=5),
                "vertex": _placement("vertex", 18, "Aries", house=7),
            }
        }
    )
    chart_b = _synthetic_chart("B")
    composite = _synthetic_chart("Composite").model_copy(
        update={
            "placements": {
                "sun": _placement("sun", 10, "Aries"),
                "eros": _placement("eros", 11, "Aries"),
                "psyche": _placement("psyche", 12, "Aries"),
                "moon": _placement("moon", 80, "Gemini"),
            }
        }
    )
    relationship = RelationshipCalculation(
        person_a=chart_a,
        person_b=chart_b,
        synastry_aspects=[
            Aspect(point_a="eros", point_b="venus", aspect="conjunction", exact_angle=0, orb=0.1),
            Aspect(point_a="psyche", point_b="moon", aspect="conjunction", exact_angle=0, orb=0.1),
            Aspect(point_a="lilith", point_b="mars", aspect="conjunction", exact_angle=0, orb=0.1),
            Aspect(point_a="vertex", point_b="sun", aspect="conjunction", exact_angle=0, orb=0.1),
            Aspect(point_a="juno", point_b="chiron", aspect="conjunction", exact_angle=0, orb=0.1),
            Aspect(point_a="sun", point_b="moon", aspect="conjunction", exact_angle=0, orb=0.1),
        ],
        house_overlays=[
            HouseOverlay(
                planet_owner="person_a",
                house_owner="person_b",
                body="eros",
                house=7,
                body_longitude=15,
            ),
            HouseOverlay(
                planet_owner="person_a",
                house_owner="person_b",
                body="psyche",
                house=8,
                body_longitude=16,
            ),
        ],
        composite=composite,
        composite_aspects=[
            Aspect(point_a="eros", point_b="venus", aspect="conjunction", exact_angle=0, orb=0.1),
            Aspect(point_a="psyche", point_b="moon", aspect="conjunction", exact_angle=0, orb=0.1),
        ],
    )

    markdown = generate_relationship_report(relationship).to_markdown()
    lower_markdown = markdown.lower()

    assert "eros" not in lower_markdown
    assert "psyche" not in lower_markdown
    assert "lilith" not in lower_markdown
    assert "vertex" not in lower_markdown
    assert "juno" not in lower_markdown
    assert "chiron" not in lower_markdown
    assert "soulmate" not in lower_markdown
    assert "fated" not in lower_markdown
    assert "destined" not in lower_markdown
    assert "twin flame" not in lower_markdown
    assert "compatibility score" not in lower_markdown
    assert "A's Sun conjunct B's Moon" in markdown
    assert "eros" in relationship.person_a.placements
    assert "psyche" in relationship.person_a.placements


def test_advanced_asteroid_calculation_ids_remain_available_internally():
    from constellation_core.chart import ASTEROID_IDS

    assert "eros" in ASTEROID_IDS
    assert "psyche" in ASTEROID_IDS


def test_synthesis_packet_uses_ranked_patterns_and_lead_logic():
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("A"),
        person_b=_synthetic_chart("B"),
        synastry_aspects=[
            Aspect(point_a="mercury", point_b="mars", aspect="square", exact_angle=90, orb=0.1),
            Aspect(point_a="moon", point_b="venus", aspect="trine", exact_angle=120, orb=1.5),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )
    context = RelationshipContext(relationship_type="romantic", status="current")

    packet = build_report_synthesis_packet(relationship, context=context)

    assert [pattern.priority for pattern in packet.top_ranked_patterns] == sorted(
        [pattern.priority for pattern in packet.top_ranked_patterns], reverse=True
    )
    assert packet.top_ranked_patterns[0].key == "synastry.moon_venus"
    assert packet.lead_pattern is not None
    assert packet.lead_pattern.key == "synastry.moon_venus"
    assert any(pattern.key == "synastry.mercury_mars" for pattern in packet.top_ranked_patterns)


def test_synthesis_packet_respects_convergence_adjusted_ordering():
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("A"),
        person_b=_synthetic_chart("B"),
        synastry_aspects=[
            Aspect(point_a="mercury", point_b="mars", aspect="square", exact_angle=90, orb=0.1),
            Aspect(point_a="sun", point_b="moon", aspect="trine", exact_angle=120, orb=5.9),
            Aspect(point_a="moon", point_b="venus", aspect="trine", exact_angle=120, orb=5.9),
            Aspect(point_a="moon", point_b="mars", aspect="square", exact_angle=90, orb=5.9),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )

    packet = build_report_synthesis_packet(relationship)

    keys = [pattern.key for pattern in packet.top_ranked_patterns]
    assert keys.index("synastry.sun_moon") < keys.index("synastry.mercury_mars")
    assert keys.index("synastry.moon_venus") < keys.index("synastry.mercury_mars")
    assert packet.top_ranked_patterns[0].adjusted_priority == packet.top_ranked_patterns[0].priority


def test_synthesis_packet_excludes_default_gated_asteroid_patterns():
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("A"),
        person_b=_synthetic_chart("B"),
        synastry_aspects=[
            Aspect(point_a="eros", point_b="psyche", aspect="conjunction", exact_angle=0, orb=0.1),
            Aspect(point_a="juno", point_b="venus", aspect="conjunction", exact_angle=0, orb=0.1),
            Aspect(point_a="sun", point_b="moon", aspect="trine", exact_angle=120, orb=1.0),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )

    packet = build_report_synthesis_packet(relationship)
    text = packet.model_dump_json().lower()

    assert "eros" not in text
    assert "psyche" not in text
    assert "synastry.asteroid.juno.venus" in text


def test_saved_motif_selector_excludes_suppressed_and_asteroid_patterns():
    from constellation_core.motifs import select_motifs_for_persistence
    from constellation_core.schemas import RankedPatternSummary, ReportSynthesisPacket

    lead = RankedPatternSummary(
        key="synastry.sun_moon",
        title="Sun Moon",
        category="emotional_recognition",
        priority=95,
        adjusted_priority=95,
        confidence="high",
        layer="synastry",
    )
    suppressed = RankedPatternSummary(
        key="synastry.mercury_jupiter",
        title="Mercury Jupiter",
        category="communication_heat",
        priority=24,
        adjusted_priority=24,
        confidence="medium",
        layer="synastry",
    )
    asteroid = RankedPatternSummary(
        key="synastry.asteroid.eros.psyche",
        title="Eros Psyche",
        category="asteroid_support",
        priority=90,
        adjusted_priority=90,
        confidence="medium",
        layer="synastry",
    )
    composite = RankedPatternSummary(
        key="composite.moon_saturn",
        title="Composite Moon Saturn",
        category="stability_container",
        priority=88,
        adjusted_priority=88,
        confidence="high",
        layer="composite",
    )

    selected = select_motifs_for_persistence(
        ReportSynthesisPacket(
            top_ranked_patterns=[lead, suppressed, asteroid],
            lead_pattern=lead,
            friction_patterns=[suppressed],
            composite_themes=[composite],
        )
    )

    keys = [item.key for item in selected]
    assert keys == ["synastry.sun_moon", "composite.moon_saturn"]


def test_relationship_map_affirmative_lead_overlays_and_chart_specific_repair():
    chart_a = _synthetic_chart("Charlie").model_copy(
        update={
            "placements": {
                "sun": _placement("sun", 250, "Sagittarius", house=6),
                "moon": _placement("moon", 285, "Capricorn", house=8),
                "mercury": _placement("mercury", 252, "Sagittarius", house=6),
                "venus": _placement("venus", 182, "Libra", house=5),
                "mars": _placement("mars", 215, "Scorpio", house=5),
            }
        }
    )
    chart_b = _synthetic_chart("Ellis").model_copy(
        update={
            "placements": {
                "sun": _placement("sun", 160, "Virgo", house=5),
                "moon": _placement("moon", 44, "Taurus", house=12),
                "mercury": _placement("mercury", 165, "Virgo", house=5),
                "venus": _placement("venus", 150, "Virgo", house=5),
                "mars": _placement("mars", 185, "Libra", house=6),
            },
            "angles": {
                "ascendant": Angle(name="Ascendant", longitude=2, sign="Aries", sign_index=0, degree=2),
            },
        }
    )
    composite = _synthetic_chart("Composite").model_copy(
        update={
            "placements": {
                "sun": _placement("sun", 10, "Aries"),
                "moon": _placement("moon", 100, "Cancer"),
                "mars": _placement("mars", 280, "Capricorn"),
                "pluto": _placement("pluto", 281, "Capricorn"),
                "saturn": _placement("saturn", 190, "Libra"),
            }
        }
    )
    relationship = RelationshipCalculation(
        person_a=chart_a,
        person_b=chart_b,
        synastry_aspects=[
            Aspect(point_a="venus", point_b="ascendant", aspect="opposition", exact_angle=180, orb=0.4),
            Aspect(point_a="mercury", point_b="mercury", aspect="square", exact_angle=90, orb=0.6),
        ],
        house_overlays=[
            HouseOverlay(planet_owner="person_a", house_owner="person_b", body="venus", house=7, body_longitude=182),
            HouseOverlay(planet_owner="person_a", house_owner="person_b", body="sun", house=7, body_longitude=250),
            HouseOverlay(planet_owner="person_b", house_owner="person_a", body="moon", house=5, body_longitude=44),
        ],
        composite=composite,
        composite_aspects=[
            Aspect(point_a="sun", point_b="saturn", aspect="opposition", exact_angle=180, orb=0.3),
            Aspect(point_a="mars", point_b="pluto", aspect="conjunction", exact_angle=0, orb=0.2),
            Aspect(point_a="moon", point_b="sun", aspect="square", exact_angle=90, orb=0.5),
            Aspect(point_a="moon", point_b="saturn", aspect="square", exact_angle=90, orb=0.5),
        ],
    )

    markdown = generate_relationship_report(relationship).to_markdown()
    section_titles = [line.removeprefix("## ") for line in markdown.splitlines() if line.startswith("## ")]
    overview = markdown.split("## Overview", maxsplit=1)[1].split("## Charlie Relationship Profile", maxsplit=1)[0]
    charlie_to_ellis = markdown.split("## How Charlie Activates Ellis", maxsplit=1)[1].split("## How Ellis Activates Charlie", maxsplit=1)[0]
    ellis_to_charlie = markdown.split("## How Ellis Activates Charlie", maxsplit=1)[1].split("## Composite Field", maxsplit=1)[0]
    profiles = markdown.split("## Charlie Relationship Profile", maxsplit=1)[1].split("## How Charlie Activates Ellis", maxsplit=1)[0]
    composite_block = markdown.split("## Composite Field", maxsplit=1)[1].split("## Friction and Repair", maxsplit=1)[0]
    friction = markdown.split("## Friction and Repair", maxsplit=1)[1]

    assert section_titles.index("Calculated chart check") > section_titles.index("Friction and Repair")
    assert "Venus opposite Ellis's Ascendant" in overview.split(".", 1)[0]
    assert "Composite Sun opposite Saturn" not in overview.split(".", 1)[0]
    assert "Charlie's Venus in Ellis's 7th house" in overview
    assert "Charlie's Venus in Ellis's 7th house" in charlie_to_ellis
    assert "Charlie's Libra Venus in the 5th house" in charlie_to_ellis
    assert "Sagittarius Mercury in the 6th house" in charlie_to_ellis
    assert "Virgo Mercury in the 5th house" in charlie_to_ellis
    assert "Ellis's Moon in Charlie's 5th house" in ellis_to_charlie
    assert "5th/7th/8th-house emphasis" not in profiles
    assert "sensitivity protected by self-control" in profiles
    assert "Moon squares an opposition between Saturn and Sun" in composite_block
    assert "apex/pressure point" in composite_block
    assert "Consent, pacing, trust" in composite_block
    assert "With Mars/Pluto carrying so much charge" in friction
    assert "With Mercury/Mercury friction" in friction
    assert "compatibility score" not in markdown.lower()
    assert "soulmate" not in markdown.lower()
    assert "twin flame" not in markdown.lower()
    assert "destined" not in markdown.lower()
    assert "fated" not in markdown.lower()
    assert "meant to be" not in markdown.lower()


def test_report_dynamic_details_are_selective_natalized_and_connected():
    chart_a = _synthetic_chart("Charlie").model_copy(
        update={
            "placements": {
                "mercury": _placement("mercury", 252, "Sagittarius", house=6),
                "mars": _placement("mars", 250, "Sagittarius", house=6),
                "venus": _placement("venus", 182, "Libra", house=5),
            }
        }
    )
    chart_b = _synthetic_chart("Ellis").model_copy(
        update={
            "placements": {
                "mercury": _placement("mercury", 165, "Virgo", house=5),
                "mars": _placement("mars", 185, "Libra", house=6),
                "venus": _placement("venus", 150, "Virgo", house=5),
            }
        }
    )
    composite = _synthetic_chart("Composite").model_copy(
        update={
            "placements": {
                "sun": _placement("sun", 10, "Aries"),
                "moon": _placement("moon", 100, "Cancer"),
                "saturn": _placement("saturn", 190, "Libra"),
                "mars": _placement("mars", 280, "Capricorn"),
                "pluto": _placement("pluto", 281, "Capricorn"),
            }
        }
    )
    relationship = RelationshipCalculation(
        person_a=chart_a,
        person_b=chart_b,
        synastry_aspects=[
            Aspect(point_a="mars", point_b="mercury", aspect="square", exact_angle=90, orb=0.2),
            Aspect(point_a="mercury", point_b="mercury", aspect="square", exact_angle=90, orb=0.4),
            Aspect(point_a="venus", point_b="mars", aspect="sextile", exact_angle=60, orb=5.8),
        ],
        house_overlays=[HouseOverlay(planet_owner="person_a", house_owner="person_b", body="venus", house=7, body_longitude=182)],
        composite=composite,
        composite_aspects=[
            Aspect(point_a="sun", point_b="saturn", aspect="opposition", exact_angle=180, orb=0.3),
            Aspect(point_a="moon", point_b="sun", aspect="square", exact_angle=90, orb=0.5),
            Aspect(point_a="moon", point_b="saturn", aspect="square", exact_angle=90, orb=0.5),
            Aspect(point_a="mars", point_b="pluto", aspect="conjunction", exact_angle=0, orb=0.2),
        ],
    )

    report = generate_relationship_report(relationship)
    details = report.dynamic_details
    all_text = " ".join([detail.read_more for detail in details] + [" ".join(detail.technical_factors) for detail in details])

    assert 1 <= len(details) < 10
    assert any(detail.kind == "synastry_aspect" for detail in details)
    assert "Sagittarius" in all_text and "Virgo" in all_text
    assert "mutable fire" in all_text and "mutable earth" in all_text
    assert any(detail.related_dynamics for detail in details)
    assert "Generic element filler" not in all_text
    assert "right now" not in all_text.lower()
    assert "compatibility score" not in all_text.lower()
    assert "soulmate" not in all_text.lower()


def test_composite_dynamic_details_name_t_square_and_mars_pluto_repair_themes():
    composite = _synthetic_chart("Composite").model_copy(
        update={
            "placements": {
                "sun": _placement("sun", 10, "Aries"),
                "moon": _placement("moon", 100, "Cancer"),
                "saturn": _placement("saturn", 190, "Libra"),
                "mars": _placement("mars", 280, "Capricorn"),
                "pluto": _placement("pluto", 281, "Capricorn"),
            }
        }
    )
    relationship = RelationshipCalculation(
        person_a=_synthetic_chart("Charlie"),
        person_b=_synthetic_chart("Ellis"),
        synastry_aspects=[],
        composite=composite,
        composite_aspects=[
            Aspect(point_a="sun", point_b="saturn", aspect="opposition", exact_angle=180, orb=0.3),
            Aspect(point_a="moon", point_b="sun", aspect="square", exact_angle=90, orb=0.5),
            Aspect(point_a="moon", point_b="saturn", aspect="square", exact_angle=90, orb=0.5),
            Aspect(point_a="mars", point_b="pluto", aspect="conjunction", exact_angle=0, orb=0.2),
        ],
    )

    details_by_key = {detail.kind + detail.title: detail.read_more for detail in generate_relationship_report(relationship).dynamic_details}
    joined = " ".join(details_by_key.values()).lower()

    assert "opposition" in joined and "apex" in joined and "pressure point" in joined
    assert "pacing" in joined and "trust" in joined and "power" in joined and "escalate" in joined


def test_temperament_helpers_and_packet_surface_compact_translation_context():
    from constellation_core.temperament import chart_temperament_summary, compare_temperaments

    chart_a = _synthetic_chart("A").model_copy(
        update={
            "placements": {
                "sun": _placement("sun", 250, "Sagittarius", house=6),
                "moon": _placement("moon", 285, "Capricorn", house=8),
                "mercury": _placement("mercury", 252, "Sagittarius", house=6),
                "venus": _placement("venus", 182, "Libra", house=5),
                "mars": _placement("mars", 215, "Scorpio", house=5),
            }
        }
    )
    chart_b = _synthetic_chart("B").model_copy(
        update={
            "placements": {
                "sun": _placement("sun", 160, "Virgo", house=5),
                "moon": _placement("moon", 75, "Gemini", house=4),
                "mercury": _placement("mercury", 165, "Virgo", house=5),
                "venus": _placement("venus", 150, "Virgo", house=5),
                "mars": _placement("mars", 185, "Libra", house=6),
            }
        }
    )
    relationship = RelationshipCalculation(
        person_a=chart_a,
        person_b=chart_b,
        synastry_aspects=[Aspect(point_a="mercury", point_b="mercury", aspect="square", exact_angle=90, orb=0.6)],
    )

    a_summary = chart_temperament_summary(chart_a)
    comparison = compare_temperaments(chart_a, chart_b)
    packet = build_report_synthesis_packet(relationship)
    diagnostics = __import__("constellation_core.report", fromlist=["build_report_diagnostics"]).build_report_diagnostics(relationship)

    assert a_summary["elements"]["fire"] >= 2
    assert a_summary["modalities"]["mutable"] >= 2
    assert a_summary["moon"] == {"sign": "Capricorn", "element": "earth", "modality": "cardinal", "house": 8}
    assert "mutable" in comparison["shared_modalities"]
    assert packet.temperament_summary is not None
    assert packet.temperament_summary["person_a"]["mercury"]["element"] == "fire"
    assert diagnostics.temperament_summary is not None
    assert diagnostics.ai_synthesis_packet_summary["has_temperament_summary"] is True


def test_temperament_weaves_mercury_detail_moon_profile_repair_and_prompt_guardrail():
    from constellation_core.ai_enhancement import AI_ENHANCEMENT_SYSTEM_PROMPT

    chart_a = _synthetic_chart("Charlie").model_copy(
        update={
            "placements": {
                "sun": _placement("sun", 250, "Sagittarius", house=6),
                "moon": _placement("moon", 285, "Capricorn", house=8),
                "mercury": _placement("mercury", 252, "Sagittarius", house=6),
                "venus": _placement("venus", 182, "Libra", house=5),
                "mars": _placement("mars", 215, "Scorpio", house=5),
            }
        }
    )
    chart_b = _synthetic_chart("Ellis").model_copy(
        update={
            "placements": {
                "sun": _placement("sun", 160, "Virgo", house=5),
                "moon": _placement("moon", 75, "Gemini", house=4),
                "mercury": _placement("mercury", 165, "Virgo", house=5),
                "venus": _placement("venus", 150, "Virgo", house=5),
                "mars": _placement("mars", 185, "Libra", house=6),
            }
        }
    )
    relationship = RelationshipCalculation(
        person_a=chart_a,
        person_b=chart_b,
        synastry_aspects=[Aspect(point_a="mercury", point_b="mercury", aspect="square", exact_angle=90, orb=0.6)],
    )

    report = generate_relationship_report(relationship)
    markdown = report.to_markdown()
    mercury_detail = next(detail for detail in report.dynamic_details if "Mercury" in detail.title)

    assert "mutable fire" in mercury_detail.read_more
    assert "mutable earth" in mercury_detail.read_more
    assert "Sagittarius Mercury in the 6th house" in mercury_detail.read_more
    assert "Virgo Mercury in the 5th house" in mercury_detail.read_more
    assert "Capricorn" in markdown and "cardinal earth emotional style" in markdown
    assert "Gemini" in markdown and "mutable air emotional style" in markdown
    assert "Where Mercury is emphasized, repair works best through precision" in markdown
    assert "Fire signs are passionate and earth signs are practical" not in markdown
    assert "compatibility score" not in markdown.lower()
    assert "soulmate" not in markdown.lower()
    assert "twin flame" not in markdown.lower()
    assert "unless they are supplied by deterministic temperament data" in AI_ENHANCEMENT_SYSTEM_PROMPT


def test_relationship_ruler_context_surfaces_in_report_detail_diagnostics_and_packet():
    chart_a = _synthetic_chart("Charlie").model_copy(update={"placements": {"venus": _placement("venus", 280, "Capricorn", house=6)}})
    chart_b = _synthetic_chart("Ellis").model_copy(update={"placements": {"saturn": _placement("saturn", 281, "Capricorn", house=6), "mars": _placement("mars", 215, "Scorpio", house=5)}, "angles": {"ascendant": Angle(name="Ascendant", longitude=90, sign="Cancer", sign_index=3, degree=0)}})
    relationship = RelationshipCalculation(person_a=chart_a, person_b=chart_b, synastry_aspects=[Aspect(point_a="venus", point_b="saturn", aspect="conjunction", exact_angle=0, orb=0.5)], house_overlays=[])

    report = generate_relationship_report(relationship)
    detail_text = " ".join(detail.read_more for detail in report.dynamic_details)
    diagnostics = build_report_diagnostics(relationship)
    packet = build_report_synthesis_packet(relationship)

    assert "7th-house ruler" in report.to_markdown()
    assert "chart-specific relationship significator" in detail_text
    assert diagnostics.relationship_rulership_summary["person_b"]["relationship_axis"]["descendant_ruler"]["planet"] == "Saturn"
    assert diagnostics.relationship_rulership_summary["cross_activations"]
    assert packet.relationship_rulership_summary["cross_activations"]
    joined = report.to_markdown().lower() + detail_text.lower()
    assert "compatibility score" not in joined
    assert "soulmate" not in joined
    assert "twin flame" not in joined
    assert "destined" not in joined
    assert "fated" not in joined
    assert "meant to be" not in joined
