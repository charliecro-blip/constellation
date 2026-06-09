from constellation_core.constellation_patterns import (
    RelationshipPatternInput,
    build_constellation_pattern_summary,
)
from constellation_core.patterns import detect_relationship_patterns
from constellation_core.relationship import calculate_relationship
from constellation_core.schemas import BirthData


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
