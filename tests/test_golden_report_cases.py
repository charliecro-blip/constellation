"""Golden Relationship Map fixtures for compact report-priority QA.

These tests protect report-priority doctrine without requiring manual report
reading. They assert diagnostics, synthesis-packet ordering, persisted motifs,
and safety-language boundaries instead of snapshotting full Markdown reports.
"""

from __future__ import annotations

import pytest

from constellation_core.constellation_patterns import (
    RelationshipPatternInput,
    build_constellation_pattern_summary,
)
from constellation_core.report import build_report_diagnostics, generate_relationship_report
from fixtures.relationship_cases import GOLDEN_RELATIONSHIP_CASES, RelationshipGoldenCase

FORBIDDEN_REPORT_LANGUAGE = [
    "compatibility score",
    "meant-to-be",
    "meant to be",
    "soulmate",
    "fated",
    "destined",
]


def compact_report_snapshot(case: RelationshipGoldenCase, *, context_name: str | None = None) -> dict[str, object]:
    """Return a compact deterministic report snapshot for golden-fixture assertions."""

    context = case.alternate_contexts[context_name] if context_name else case.context
    diagnostics = build_report_diagnostics(case.relationship, context)
    synthesis = diagnostics.ai_synthesis_packet_summary or {}
    return {
        "house_system": diagnostics.house_system,
        "lead_pattern": diagnostics.selected_lead_pattern.key if diagnostics.selected_lead_pattern else None,
        "lead_category": diagnostics.selected_lead_pattern.category if diagnostics.selected_lead_pattern else None,
        "top_categories": [pattern.category for pattern in diagnostics.top_ranked_patterns[:3]],
        "top_pattern_keys": [pattern.key for pattern in diagnostics.top_ranked_patterns[:3]],
        "mercury_mars_led": diagnostics.selected_lead_pattern is not None
        and diagnostics.selected_lead_pattern.key == "synastry.mercury_mars",
        "public_life_led": diagnostics.selected_lead_pattern is not None
        and diagnostics.selected_lead_pattern.category == "public_life",
        "synthesis_lead": synthesis.get("lead_pattern_key"),
        "motif_categories": [pattern.category for pattern in diagnostics.motif_persistence_summary],
        "included_asteroids": [
            pattern.key for pattern in diagnostics.asteroid_policy_summary.included_asteroid_patterns
        ],
        "suppressed_advanced_asteroids": diagnostics.asteroid_policy_summary.advanced_asteroids_suppressed,
        "suppressed_asteroid_notes": diagnostics.asteroid_policy_summary.suppressed_asteroid_patterns,
        "chart_sanity_exists": bool(
            diagnostics.person_a_chart_sanity.sun
            and diagnostics.person_a_chart_sanity.moon
            and diagnostics.person_a_chart_sanity.ascendant
            and diagnostics.person_b_chart_sanity.sun
            and diagnostics.person_b_chart_sanity.moon
            and diagnostics.person_b_chart_sanity.ascendant
        ),
    }


@pytest.mark.parametrize("case_name", GOLDEN_RELATIONSHIP_CASES.keys())
def test_golden_cases_have_placidus_chart_sanity_and_synthesis_packet(case_name: str):
    snapshot = compact_report_snapshot(GOLDEN_RELATIONSHIP_CASES[case_name])

    assert snapshot["house_system"] == "placidus"
    assert snapshot["chart_sanity_exists"] is True
    assert snapshot["synthesis_lead"] == snapshot["lead_pattern"]


def test_emotional_recognition_leads_over_minor_communication_heat():
    snapshot = compact_report_snapshot(GOLDEN_RELATIONSHIP_CASES["emotional_recognition_leads"])

    assert snapshot["lead_category"] == "emotional_recognition"
    assert snapshot["lead_pattern"] == "synastry.sun_moon"
    assert "communication_heat" in snapshot["top_categories"]
    assert snapshot["mercury_mars_led"] is False


def test_communication_context_can_elevate_mercury_mars():
    snapshot = compact_report_snapshot(GOLDEN_RELATIONSHIP_CASES["communication_context_exception"])

    assert snapshot["lead_pattern"] == "synastry.mercury_mars"
    assert snapshot["lead_category"] == "communication_heat"
    assert snapshot["mercury_mars_led"] is True


def test_public_life_does_not_lead_romance_but_can_lead_work_context():
    case = GOLDEN_RELATIONSHIP_CASES["public_life_context_exception"]
    romantic = compact_report_snapshot(case)
    work = compact_report_snapshot(case, context_name="work")

    assert romantic["lead_category"] == "emotional_recognition"
    assert romantic["public_life_led"] is False
    assert "public_life" in romantic["top_categories"]
    assert work["lead_category"] == "public_life"
    assert work["public_life_led"] is True


def test_trust_depth_is_central_and_persisted_as_structured_motif():
    snapshot = compact_report_snapshot(GOLDEN_RELATIONSHIP_CASES["trust_depth_persists"])

    assert "trust_depth" in snapshot["top_categories"]
    assert "trust_depth" in snapshot["motif_categories"]


def test_saturn_container_generates_repair_language():
    case = GOLDEN_RELATIONSHIP_CASES["saturn_container_repair"]
    snapshot = compact_report_snapshot(case)
    markdown = generate_relationship_report(case.relationship, context=case.context).to_markdown()
    friction = markdown.split("## Friction and Repair", maxsplit=1)[1]

    assert snapshot["lead_category"] == "stability_container"
    assert "stability_container" in snapshot["motif_categories"]
    assert "supportive or restrictive" in friction
    assert "name expectations directly" in friction


def test_asteroid_gating_surfaces_mvp_and_suppresses_advanced_default_points():
    case = GOLDEN_RELATIONSHIP_CASES["asteroid_gating"]
    snapshot = compact_report_snapshot(case)
    markdown = generate_relationship_report(case.relationship, context=case.context).to_markdown().lower()

    assert "synastry.asteroid.juno.venus" in snapshot["included_asteroids"]
    assert {"eros", "psyche", "lilith", "vertex"}.issubset(
        set(snapshot["suppressed_advanced_asteroids"])
    )
    assert any("eros" in note for note in snapshot["suppressed_asteroid_notes"])
    assert any("psyche" in note for note in snapshot["suppressed_asteroid_notes"])
    assert "eros" not in markdown
    assert "psyche" not in markdown
    assert "lilith" not in markdown
    assert "vertex" not in markdown


@pytest.mark.parametrize("case_name", GOLDEN_RELATIONSHIP_CASES.keys())
def test_golden_reports_avoid_score_and_fate_language(case_name: str):
    case = GOLDEN_RELATIONSHIP_CASES[case_name]
    markdown = generate_relationship_report(case.relationship, context=case.context).to_markdown().lower()

    for phrase in FORBIDDEN_REPORT_LANGUAGE:
        assert phrase not in markdown


def test_golden_motif_snapshots_feed_constellation_pattern_aggregation():
    trust_snapshot = compact_report_snapshot(GOLDEN_RELATIONSHIP_CASES["trust_depth_persists"])
    saturn_snapshot = compact_report_snapshot(GOLDEN_RELATIONSHIP_CASES["saturn_container_repair"])
    emotional_snapshot = compact_report_snapshot(GOLDEN_RELATIONSHIP_CASES["emotional_recognition_leads"])

    summary = build_constellation_pattern_summary(
        [
            RelationshipPatternInput(
                relationship_id="golden-trust",
                relationship_type="romantic",
                person_name="Trust Fixture",
                structured_motifs=[
                    {
                        "key": key,
                        "category": category,
                        "title": category,
                        "relationship_id": "golden-trust",
                    }
                    for key, category in zip(
                        trust_snapshot["top_pattern_keys"], trust_snapshot["motif_categories"], strict=False
                    )
                ],
            ),
            RelationshipPatternInput(
                relationship_id="golden-saturn",
                relationship_type="romantic",
                person_name="Saturn Fixture",
                structured_motifs=[
                    {
                        "key": "synastry.moon_saturn",
                        "category": category,
                        "title": category,
                        "relationship_id": "golden-saturn",
                    }
                    for category in saturn_snapshot["motif_categories"]
                ],
            ),
            RelationshipPatternInput(
                relationship_id="golden-emotional",
                relationship_type="romantic",
                person_name="Recognition Fixture",
                structured_motifs=[
                    {
                        "key": "synastry.sun_moon",
                        "category": category,
                        "title": category,
                        "relationship_id": "golden-emotional",
                    }
                    for category in emotional_snapshot["motif_categories"]
                ],
            ),
        ]
    )

    motif_ids = {motif["id"] for motif in summary["recurring_motifs"]}
    assert summary["has_enough_data"] is True
    assert "emotional_recognition" in motif_ids
    assert any(item["category"] == "emotional_recognition" for item in summary["top_motif_categories"])
