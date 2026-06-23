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


def test_constellation_patterns_prefer_structured_motifs_and_group_people_by_category():
    summary = build_constellation_pattern_summary([
        RelationshipPatternInput(
            relationship_id="rel-eva",
            relationship_type="romantic",
            person_name="Eva",
            report_markdown="Saturn appears in prose but should not drive structured aggregation.",
            structured_motifs=[
                {
                    "key": "synastry.moon_saturn",
                    "category": "stability_container",
                    "title": "Moon Saturn",
                    "relationship_id": "rel-eva",
                },
                {
                    "key": "composite.moon_saturn",
                    "category": "stability_container",
                    "title": "Composite Moon Saturn",
                    "relationship_id": "rel-eva",
                },
            ],
        ),
        RelationshipPatternInput(
            relationship_id="rel-tess",
            relationship_type="friend",
            person_name="Tess",
            structured_motifs=[
                {
                    "key": "synastry.venus_saturn",
                    "category": "stability_container",
                    "title": "Venus Saturn",
                    "relationship_id": "rel-tess",
                }
            ],
        ),
        RelationshipPatternInput(
            relationship_id="rel-anna",
            relationship_type="collaborator",
            person_name="Anna",
            structured_motifs=[
                {
                    "key": "synastry.sun_moon",
                    "category": "emotional_recognition",
                    "title": "Sun Moon",
                    "relationship_id": "rel-anna",
                }
            ],
        ),
    ])

    motifs = {item["id"]: item for item in summary["recurring_motifs"]}
    assert motifs["stability_container"]["label"] == "Stability / Container"
    assert motifs["stability_container"]["people"] == ["Eva", "Tess"]
    assert motifs["stability_container"]["count"] == 2
    assert motifs["stability_container"]["relationship_ids"] == ["rel-eva", "rel-tess"]
    assert "saturn" not in motifs
    assert summary["top_motif_categories"][0] == {
        "category": "stability_container",
        "label": "Stability / Container",
        "description": "Where commitment, time, limits, or responsibility shape the bond.",
        "count": 2,
    }
    assert motifs["stability_container"]["description"] == (
        "Where commitment, time, limits, or responsibility shape the bond."
    )
    assert "Your saved maps currently emphasize" in summary["plain_language_summary"]


def test_relationship_house_rulerships_and_activation_detection():
    from constellation_core.rulerships import relationship_significator_summary, sign_ruler
    from constellation_core.schemas import Angle, Aspect, BirthData, Chart, Placement, RelationshipCalculation
    from constellation_core.patterns import detect_relationship_patterns

    birth = BirthData(name="A", date="1990-01-01", time="12:00", latitude=0, longitude=0, timezone="UTC")

    def placement(body, longitude, sign, house=None):
        return Placement(body=body, longitude=longitude, sign=sign, sign_index=int(longitude // 30), degree=longitude % 30, house=house)

    a = Chart(name="A", birth=birth, julian_day_ut=None, house_system="whole_sign", placements={"venus": placement("venus", 280, "Capricorn", 6)}, angles={"ascendant": Angle(name="Ascendant", longitude=90, sign="Cancer", sign_index=3, degree=0)})
    b = Chart(name="B", birth=birth.model_copy(update={"name": "B"}), julian_day_ut=None, house_system="whole_sign", placements={"saturn": placement("saturn", 281, "Capricorn", 6), "mars": placement("mars", 215, "Scorpio", 5)}, angles={"ascendant": Angle(name="Ascendant", longitude=90, sign="Cancer", sign_index=3, degree=0)})
    relationship = RelationshipCalculation(person_a=a, person_b=b, synastry_aspects=[Aspect(point_a="venus", point_b="saturn", aspect="conjunction", exact_angle=0, orb=0.5)], house_overlays=[])

    summary = relationship_significator_summary(b)
    assert sign_ruler("Capricorn") == "saturn"
    assert summary["relationship_axis"]["descendant"] == "Capricorn"
    assert summary["relationship_axis"]["descendant_ruler"]["planet"] == "Saturn"
    assert summary["romance_significator"]["ruler"]["planet"] == "Mars"
    assert summary["intimacy_significator"]["ruler"]["planet"] == "Saturn"
    patterns = detect_relationship_patterns(relationship)
    assert any(pattern.key == "synastry.relationship_ruler.descendant_ruler" for pattern in patterns)
    assert any("7th-house ruler" in " ".join(pattern.evidence) for pattern in patterns)


def test_traditional_ruler_map_is_complete_and_traditional_only():
    from constellation_core.rulerships import TRADITIONAL_SIGN_RULERS

    expected = {
        "aries": "mars",
        "taurus": "venus",
        "gemini": "mercury",
        "cancer": "moon",
        "leo": "sun",
        "virgo": "mercury",
        "libra": "venus",
        "scorpio": "mars",
        "sagittarius": "jupiter",
        "capricorn": "saturn",
        "aquarius": "saturn",
        "pisces": "jupiter",
    }
    assert TRADITIONAL_SIGN_RULERS == expected
    # No modern co-rulers (uranus, neptune, pluto) in the default map.
    assert "uranus" not in TRADITIONAL_SIGN_RULERS.values()
    assert "neptune" not in TRADITIONAL_SIGN_RULERS.values()
    assert "pluto" not in TRADITIONAL_SIGN_RULERS.values()


def test_rulership_layer_skipped_when_house_data_missing():
    from constellation_core.rulerships import relationship_house_rulers, relationship_significator_summary
    from constellation_core.schemas import BirthData, Chart

    birth = BirthData(name="X", date="1990-01-01", time="12:00", latitude=0, longitude=0, timezone="UTC")
    chart_no_angles = Chart(
        name="X", birth=birth, julian_day_ut=None, house_system="whole_sign",
        placements={}, angles={},
    )
    rulers = relationship_house_rulers(chart_no_angles)
    assert rulers == {}

    summary = relationship_significator_summary(chart_no_angles)
    assert summary["relationship_axis"]["ascendant"] is None
    assert summary["relationship_axis"]["ascendant_ruler"] is None


def test_5th_and_8th_ruler_contacts_detected():
    from constellation_core.schemas import Angle, Aspect, BirthData, Chart, Placement, RelationshipCalculation

    birth = BirthData(name="A", date="1990-01-01", time="12:00", latitude=0, longitude=0, timezone="UTC")

    def placement(body, longitude, sign, house=None):
        return Placement(body=body, longitude=longitude, sign=sign, sign_index=int(longitude // 30), degree=longitude % 30, house=house)

    # B has Cancer Asc → 5th house Scorpio (ruler Mars), 8th house Aquarius (ruler Saturn).
    a = Chart(
        name="A", birth=birth, julian_day_ut=None, house_system="whole_sign",
        placements={"moon": placement("moon", 215, "Scorpio", 5)},
        angles={"ascendant": Angle(name="Ascendant", longitude=90, sign="Cancer", sign_index=3, degree=0)},
    )
    b = Chart(
        name="B", birth=birth.model_copy(update={"name": "B"}), julian_day_ut=None, house_system="whole_sign",
        placements={
            "mars": placement("mars", 210, "Scorpio", 5),
            "saturn": placement("saturn", 300, "Aquarius", 8),
        },
        angles={"ascendant": Angle(name="Ascendant", longitude=90, sign="Cancer", sign_index=3, degree=0)},
    )
    # A's Moon conjuncts B's Mars (5th ruler) and A's Moon also trines B's Saturn (8th ruler).
    relationship = RelationshipCalculation(
        person_a=a, person_b=b,
        synastry_aspects=[
            Aspect(point_a="moon", point_b="mars", aspect="conjunction", exact_angle=0, orb=0.8),
            Aspect(point_a="moon", point_b="saturn", aspect="trine", exact_angle=0, orb=1.2),
        ],
        house_overlays=[],
    )
    patterns = detect_relationship_patterns(relationship)
    keys = [p.key for p in patterns]
    assert "synastry.relationship_ruler.romance_ruler" in keys
    assert "synastry.relationship_ruler.intimacy_ruler" in keys


def test_reciprocal_7th_ruler_detected_when_both_contacted():
    from constellation_core.schemas import Angle, Aspect, BirthData, Chart, Placement, RelationshipCalculation

    birth = BirthData(name="A", date="1990-01-01", time="12:00", latitude=0, longitude=0, timezone="UTC")

    def placement(body, longitude, sign, house=None):
        return Placement(body=body, longitude=longitude, sign=sign, sign_index=int(longitude // 30), degree=longitude % 30, house=house)

    # Both have Cancer Asc → Capricorn Desc (Saturn rules 7th for both).
    a = Chart(
        name="A", birth=birth, julian_day_ut=None, house_system="whole_sign",
        placements={"venus": placement("venus", 280, "Capricorn", 7), "saturn": placement("saturn", 282, "Capricorn", 7)},
        angles={"ascendant": Angle(name="Ascendant", longitude=90, sign="Cancer", sign_index=3, degree=0)},
    )
    b = Chart(
        name="B", birth=birth.model_copy(update={"name": "B"}), julian_day_ut=None, house_system="whole_sign",
        placements={"venus": placement("venus", 280, "Capricorn", 7), "saturn": placement("saturn", 282, "Capricorn", 7)},
        angles={"ascendant": Angle(name="Ascendant", longitude=90, sign="Cancer", sign_index=3, degree=0)},
    )
    # A's Venus contacts B's Saturn (B's 7th ruler); B's Venus contacts A's Saturn (A's 7th ruler).
    relationship = RelationshipCalculation(
        person_a=a, person_b=b,
        synastry_aspects=[
            Aspect(point_a="venus", point_b="saturn", aspect="conjunction", exact_angle=0, orb=0.5),
            Aspect(point_a="saturn", point_b="venus", aspect="conjunction", exact_angle=0, orb=0.5),
        ],
        house_overlays=[],
    )
    patterns = detect_relationship_patterns(relationship)
    assert any(p.key == "synastry.relationship_ruler.reciprocal_7th" for p in patterns)


def test_reciprocal_asc_ruler_detected_when_both_asc_rulers_contacted():
    from constellation_core.schemas import Angle, Aspect, BirthData, Chart, Placement, RelationshipCalculation

    birth = BirthData(name="A", date="1990-01-01", time="12:00", latitude=0, longitude=0, timezone="UTC")

    def placement(body, longitude, sign, house=None):
        return Placement(body=body, longitude=longitude, sign=sign, sign_index=int(longitude // 30), degree=longitude % 30, house=house)

    # A: Aries Asc → Mars rules Asc. B: Taurus Asc → Venus rules Asc.
    a = Chart(
        name="A", birth=birth, julian_day_ut=None, house_system="whole_sign",
        placements={"mars": placement("mars", 30, "Taurus", 2), "venus": placement("venus", 40, "Taurus", 2)},
        angles={"ascendant": Angle(name="Ascendant", longitude=0, sign="Aries", sign_index=0, degree=0)},
    )
    b = Chart(
        name="B", birth=birth.model_copy(update={"name": "B"}), julian_day_ut=None, house_system="whole_sign",
        placements={"venus": placement("venus", 30, "Taurus", 1), "mars": placement("mars", 1, "Aries", 12)},
        angles={"ascendant": Angle(name="Ascendant", longitude=30, sign="Taurus", sign_index=1, degree=0)},
    )
    # A's Venus (=B's Asc ruler) contacts B's Mars; B's Mars (=A's Asc ruler) contacts A's Venus.
    relationship = RelationshipCalculation(
        person_a=a, person_b=b,
        synastry_aspects=[
            Aspect(point_a="venus", point_b="mars", aspect="conjunction", exact_angle=0, orb=1.0),
            Aspect(point_a="mars", point_b="venus", aspect="conjunction", exact_angle=0, orb=1.0),
        ],
        house_overlays=[],
    )
    patterns = detect_relationship_patterns(relationship)
    assert any(p.key == "synastry.relationship_ruler.reciprocal_asc" for p in patterns)


def test_ruler_contact_keys_do_not_include_composite_rulerships():
    from constellation_core.schemas import Angle, Aspect, BirthData, Chart, Placement, RelationshipCalculation

    birth = BirthData(name="A", date="1990-01-01", time="12:00", latitude=0, longitude=0, timezone="UTC")

    def placement(body, longitude, sign, house=None):
        return Placement(body=body, longitude=longitude, sign=sign, sign_index=int(longitude // 30), degree=longitude % 30, house=house)

    a = Chart(name="A", birth=birth, julian_day_ut=None, house_system="whole_sign",
              placements={"venus": placement("venus", 280, "Capricorn", 7)},
              angles={"ascendant": Angle(name="Ascendant", longitude=90, sign="Cancer", sign_index=3, degree=0)})
    b = Chart(name="B", birth=birth.model_copy(update={"name": "B"}), julian_day_ut=None, house_system="whole_sign",
              placements={"saturn": placement("saturn", 281, "Capricorn", 7)},
              angles={"ascendant": Angle(name="Ascendant", longitude=90, sign="Cancer", sign_index=3, degree=0)})
    relationship = RelationshipCalculation(
        person_a=a, person_b=b,
        synastry_aspects=[Aspect(point_a="venus", point_b="saturn", aspect="conjunction", exact_angle=0, orb=0.5)],
        house_overlays=[],
    )
    patterns = detect_relationship_patterns(relationship)
    composite_ruler_keys = [p.key for p in patterns if "composite" in p.key and "ruler" in p.key]
    assert composite_ruler_keys == []


def test_sun_sun_conjunction_detected_at_low_priority():
    from constellation_core.schemas import Aspect, BirthData, Chart, Placement, RelationshipCalculation

    birth = BirthData(name="A", date="1990-01-01", time="12:00", latitude=0, longitude=0, timezone="UTC")

    def placement(body, longitude, sign, house=None):
        return Placement(body=body, longitude=longitude, sign=sign, sign_index=int(longitude // 30), degree=longitude % 30, house=house)

    a = Chart(name="A", birth=birth, julian_day_ut=None, house_system="whole_sign",
              placements={"sun": placement("sun", 15, "Aries", 1)}, angles={})
    b = Chart(name="B", birth=birth.model_copy(update={"name": "B"}), julian_day_ut=None, house_system="whole_sign",
              placements={"sun": placement("sun", 16, "Aries", 1)}, angles={})
    relationship = RelationshipCalculation(
        person_a=a, person_b=b,
        synastry_aspects=[Aspect(point_a="sun", point_b="sun", aspect="conjunction", exact_angle=0, orb=1.0)],
        house_overlays=[],
    )
    patterns = detect_relationship_patterns(relationship)
    sun_sun = next((p for p in patterns if p.key == "synastry.sun_sun_conjunction"), None)
    assert sun_sun is not None
    # Base priority 55 + _bonus(orb=1.0)=9 = 64; must stay below 70.
    assert sun_sun.priority < 70


def test_mars_mars_opposition_detected_with_sign_note():
    from constellation_core.schemas import Aspect, BirthData, Chart, Placement, RelationshipCalculation

    birth = BirthData(name="A", date="1990-01-01", time="12:00", latitude=0, longitude=0, timezone="UTC")

    def placement(body, longitude, sign, house=None):
        return Placement(body=body, longitude=longitude, sign=sign, sign_index=int(longitude // 30), degree=longitude % 30, house=house)

    a = Chart(name="A", birth=birth, julian_day_ut=None, house_system="whole_sign",
              placements={"mars": placement("mars", 210, "Scorpio", 1)}, angles={})
    b = Chart(name="B", birth=birth.model_copy(update={"name": "B"}), julian_day_ut=None, house_system="whole_sign",
              placements={"mars": placement("mars", 30, "Taurus", 7)}, angles={})
    relationship = RelationshipCalculation(
        person_a=a, person_b=b,
        synastry_aspects=[Aspect(point_a="mars", point_b="mars", aspect="opposition", exact_angle=0, orb=1.5)],
        house_overlays=[],
    )
    patterns = detect_relationship_patterns(relationship)
    mm = next((p for p in patterns if p.key == "synastry.mars_mars_opposition"), None)
    assert mm is not None
    assert "mars signs:" in " ".join(mm.evidence).lower()
    assert "scorpio" in " ".join(mm.evidence).lower()
    assert "taurus" in " ".join(mm.evidence).lower()


def test_stellium_gap_detected_when_partner_has_no_planet_in_sign():
    from constellation_core.schemas import BirthData, Chart, Placement, RelationshipCalculation

    birth = BirthData(name="A", date="1990-01-01", time="12:00", latitude=0, longitude=0, timezone="UTC")

    def placement(body, longitude, sign, house=None):
        return Placement(body=body, longitude=longitude, sign=sign, sign_index=int(longitude // 30), degree=longitude % 30, house=house)

    # A has Sun, Moon, Venus all in Taurus; B has no Taurus planets.
    a = Chart(name="A", birth=birth, julian_day_ut=None, house_system="whole_sign",
              placements={
                  "sun": placement("sun", 40, "Taurus", 1),
                  "moon": placement("moon", 45, "Taurus", 1),
                  "venus": placement("venus", 50, "Taurus", 1),
              }, angles={})
    b = Chart(name="B", birth=birth.model_copy(update={"name": "B"}), julian_day_ut=None, house_system="whole_sign",
              placements={"sun": placement("sun", 100, "Cancer", 3)}, angles={})
    relationship = RelationshipCalculation(person_a=a, person_b=b, synastry_aspects=[], house_overlays=[])

    patterns = detect_relationship_patterns(relationship)
    gap = next((p for p in patterns if p.key == "synastry.stellium_resonance.missing"), None)
    assert gap is not None
    assert gap.priority == 40
    assert gap.category == "informational"
    assert "Taurus" in gap.title


def test_stellium_gap_not_detected_when_partner_has_planet_in_sign():
    from constellation_core.schemas import BirthData, Chart, Placement, RelationshipCalculation

    birth = BirthData(name="A", date="1990-01-01", time="12:00", latitude=0, longitude=0, timezone="UTC")

    def placement(body, longitude, sign, house=None):
        return Placement(body=body, longitude=longitude, sign=sign, sign_index=int(longitude // 30), degree=longitude % 30, house=house)

    a = Chart(name="A", birth=birth, julian_day_ut=None, house_system="whole_sign",
              placements={
                  "sun": placement("sun", 40, "Taurus", 1),
                  "moon": placement("moon", 45, "Taurus", 1),
                  "venus": placement("venus", 50, "Taurus", 1),
              }, angles={})
    # B has Mars in Taurus — gap should not fire.
    b = Chart(name="B", birth=birth.model_copy(update={"name": "B"}), julian_day_ut=None, house_system="whole_sign",
              placements={"mars": placement("mars", 42, "Taurus", 1)}, angles={})
    relationship = RelationshipCalculation(person_a=a, person_b=b, synastry_aspects=[], house_overlays=[])

    patterns = detect_relationship_patterns(relationship)
    assert not any(p.key == "synastry.stellium_resonance.missing" for p in patterns)


def test_stellium_gap_does_not_reach_synthesis_packet_threshold():
    """Stellium gap is diagnostics-only; priority 40 must stay below the synthesis packet threshold (70)."""
    from constellation_core.schemas import BirthData, Chart, Placement, RelationshipCalculation
    from constellation_core.weighting import weight_patterns

    birth = BirthData(name="A", date="1990-01-01", time="12:00", latitude=0, longitude=0, timezone="UTC")

    def placement(body, longitude, sign, house=None):
        return Placement(body=body, longitude=longitude, sign=sign, sign_index=int(longitude // 30), degree=longitude % 30, house=house)

    a = Chart(name="A", birth=birth, julian_day_ut=None, house_system="whole_sign",
              placements={
                  "sun": placement("sun", 40, "Taurus", 1),
                  "moon": placement("moon", 45, "Taurus", 1),
                  "venus": placement("venus", 50, "Taurus", 1),
              }, angles={})
    b = Chart(name="B", birth=birth.model_copy(update={"name": "B"}), julian_day_ut=None, house_system="whole_sign",
              placements={"sun": placement("sun", 100, "Cancer", 3)}, angles={})
    relationship = RelationshipCalculation(person_a=a, person_b=b, synastry_aspects=[], house_overlays=[])

    patterns = detect_relationship_patterns(relationship)
    weighted = weight_patterns(patterns)
    gap_patterns = [p for p in weighted if p.key == "synastry.stellium_resonance.missing"]
    assert gap_patterns
    for gap in gap_patterns:
        assert gap.priority < 70
