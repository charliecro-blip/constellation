from constellation_core.constellation_patterns import (
    RelationshipPatternInput,
    build_constellation_pattern_summary,
)
from constellation_core.patterns import detect_relationship_patterns
from constellation_core.relationship import calculate_relationship
from constellation_core.schemas import Aspect, BirthData, Chart, Placement, RelationshipCalculation


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


def test_constellation_patterns_empty_state_when_fewer_than_two_relationships():
    summary = build_constellation_pattern_summary([
        RelationshipPatternInput(relationship_type="friend", person_name="Tess")
    ])

    assert summary["has_enough_data"] is False
    assert summary["empty_state"] == (
        "Save two or more relationships to see recurring patterns across your constellation."
    )
    assert summary["recurring_motifs"] == []


def test_constellation_patterns_counts_types_and_known_themes():
    summary = build_constellation_pattern_summary([
        RelationshipPatternInput(
            relationship_type="romantic",
            person_name="Tess",
            known_themes=["Attraction", "Repair"],
        ),
        RelationshipPatternInput(
            relationship_type="ex",
            person_name="Anna",
            known_themes=["attraction", "Distance"],
        ),
        RelationshipPatternInput(
            relationship_type="romantic",
            person_name="Jodie",
            known_themes=["repair"],
        ),
    ])

    assert {item["label"]: item["count"] for item in summary["relationship_type_counts"]} == {
        "Romantic / current": 2,
        "Ex": 1,
    }
    assert {item["theme"]: item["count"] for item in summary["known_theme_counts"]} == {
        "attraction": 2,
        "repair": 2,
        "distance": 1,
    }


def test_constellation_patterns_counts_markdown_motifs_and_groups_people():
    summary = build_constellation_pattern_summary([
        RelationshipPatternInput(
            relationship_type="romantic",
            person_name="Tess",
            report_markdown="## Overview\nMoon–Uranus appears with a 7th house emphasis and Composite work.",
        ),
        RelationshipPatternInput(
            relationship_type="friend",
            person_name="Anna",
            report_markdown="## Composite Field\nThe Moon-Uranus rhythm repeats near the 7th-house mirror.",
        ),
        RelationshipPatternInput(
            relationship_type="collaborator",
            person_name="Jodie",
            report_markdown="Saturn and 10th house material stand out.",
        ),
    ])

    motifs = {item["id"]: item for item in summary["recurring_motifs"]}
    assert motifs["moon_uranus"]["count"] == 2
    assert motifs["moon_uranus"]["people"] == ["Tess", "Anna"]
    assert motifs["7th_house"]["people"] == ["Tess", "Anna"]
    assert "saturn" not in motifs
    assert "partnership mirrors" in summary["plain_language_summary"]


def test_constellation_patterns_avoid_forbidden_language():
    summary = build_constellation_pattern_summary([
        RelationshipPatternInput(
            relationship_type="romantic",
            person_name="Tess",
            report_markdown="Venus and the 8th house are named.",
        ),
        RelationshipPatternInput(
            relationship_type="romantic",
            person_name="Anna",
            report_markdown="Venus repeats with the 8th-house material.",
        ),
    ])

    rendered_text = str(summary).lower()
    assert "compatibility score" not in rendered_text
    assert "meant to be" not in rendered_text
    assert "deterministic fate" not in rendered_text


def _placement(body: str, longitude: float) -> Placement:
    return Placement(
        body=body,
        longitude=longitude,
        sign="Aries",
        sign_index=0,
        degree=longitude % 30,
    )


def test_asteroid_synastry_patterns_require_tight_relevance():
    chart_a = Chart(
        name="A",
        birth=BirthData(
            name="A",
            date="1992-01-03",
            time="17:37",
            time_known=True,
            latitude=29.4252,
            longitude=-98.4946,
            timezone="America/Chicago",
        ),
        julian_day_ut=None,
        house_system="placidus",
        placements={"juno": _placement("juno", 10), "ceres": _placement("ceres", 20)},
    )
    chart_b = chart_a.model_copy(
        update={"name": "B", "placements": {"venus": _placement("venus", 11)}}
    )
    relationship = RelationshipCalculation(
        person_a=chart_a,
        person_b=chart_b,
        synastry_aspects=[
            Aspect(point_a="juno", point_b="venus", aspect="conjunction", exact_angle=0, orb=1.0),
            Aspect(point_a="ceres", point_b="venus", aspect="conjunction", exact_angle=0, orb=2.5),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )

    patterns = detect_relationship_patterns(relationship)
    titles = [pattern.title for pattern in patterns]
    assert any("Juno" in title and "Venus" in title for title in titles)
    assert not any("Ceres" in title and "Venus" in title for title in titles)


def test_pattern_registry_covers_major_existing_keys():
    from constellation_core.pattern_registry import get_pattern_metadata

    major_keys = [
        "sun_moon",
        "moon_moon",
        "venus_mars",
        "moon_venus",
        "moon_mars",
        "venus_pluto",
        "mars_pluto",
        "moon_saturn",
        "venus_saturn",
        "mars_saturn",
        "mercury_mars",
        "mercury_mercury",
        "moon_pluto",
        "venus_ascendant",
        "sun_ascendant",
        "moon_ascendant",
        "house_overlay",
        "composite.stellium.taurus",
        "composite.conjunction_cluster",
        "composite.mars_venus",
        "composite.mars_pluto",
        "composite.saturn_venus",
        "composite.saturn_sun",
        "composite.moon_saturn",
        "composite.moon_uranus",
    ]

    for key in major_keys:
        metadata = get_pattern_metadata(key)
        assert metadata.tier in {1, 2, 3, 4}
        assert metadata.category != "supporting_texture"
        assert metadata.description


def test_pattern_registry_tier_one_relationship_signatures():
    from constellation_core.pattern_registry import get_pattern_metadata

    tier_one_keys = [
        "sun_moon",
        "moon_moon",
        "venus_mars",
        "moon_saturn",
        "venus_saturn",
        "mars_saturn",
    ]

    assert {get_pattern_metadata(key).tier for key in tier_one_keys} == {1}


def test_pattern_registry_lead_eligibility_defaults():
    from constellation_core.pattern_registry import get_pattern_metadata
    from constellation_core.scoring_weights import LEAD_ELIGIBLE_CATEGORIES

    assert get_pattern_metadata("mercury_mars").lead_eligible is False
    assert get_pattern_metadata("overlay.house_10").category == "public_life"
    assert get_pattern_metadata("overlay.house_10").lead_eligible is False
    assert get_pattern_metadata("synastry.angle_midheaven_sun").lead_eligible is False
    assert LEAD_ELIGIBLE_CATEGORIES == {
        "emotional_recognition",
        "erotic_charge",
        "stability_container",
        "devotion_contract",
    }


def test_scoring_weight_constants_are_report_prioritization_only():
    from constellation_core import pattern_registry, scoring_weights

    assert scoring_weights.SUPPRESSION_THRESHOLDS == {
        "omit": 25,
        "supporting": 45,
        "brief": 70,
    }
    module_text = f"{pattern_registry.PATTERN_REGISTRY} {scoring_weights.__dict__}".lower()
    assert "compatibility score" not in module_text
    assert "meant to be" not in module_text


def test_asteroid_policy_constants_define_default_and_advanced_layers():
    from constellation_core.asteroid_policy import (
        ADVANCED_ASTEROIDS,
        DEFAULT_REPORT_ASTEROIDS,
        MVP_ASTEROIDS,
        OPTIONAL_MVP_ASTEROIDS,
    )

    assert MVP_ASTEROIDS == {"juno", "chiron", "ceres"}
    assert OPTIONAL_MVP_ASTEROIDS == {"vesta"}
    assert {"eros", "psyche", "lilith", "vertex"}.issubset(ADVANCED_ASTEROIDS)
    assert DEFAULT_REPORT_ASTEROIDS == {"juno", "chiron", "ceres", "vesta"}


def test_asteroid_to_asteroid_contacts_do_not_create_default_patterns():
    chart_a = Chart(
        name="A",
        birth=BirthData(
            name="A",
            date="1992-01-03",
            time="17:37",
            time_known=True,
            latitude=29.4252,
            longitude=-98.4946,
            timezone="America/Chicago",
        ),
        julian_day_ut=None,
        house_system="placidus",
        placements={"juno": _placement("juno", 10)},
    )
    chart_b = chart_a.model_copy(
        update={"name": "B", "placements": {"chiron": _placement("chiron", 10)}}
    )
    relationship = RelationshipCalculation(
        person_a=chart_a,
        person_b=chart_b,
        synastry_aspects=[
            Aspect(point_a="juno", point_b="chiron", aspect="conjunction", exact_angle=0, orb=0.1),
            Aspect(point_a="eros", point_b="psyche", aspect="conjunction", exact_angle=0, orb=0.1),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )

    text = " ".join(pattern.title for pattern in detect_relationship_patterns(relationship))

    assert "Juno" not in text
    assert "Chiron" not in text
    assert "Eros" not in text
    assert "Psyche" not in text
